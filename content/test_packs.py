"""Niche packs: the 99 niches + 20 business types of the Content AI training spec, the request understanding, the checker and the pack-to-site path."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from corecraft import pack_check, pack_request, pack_writer as W
from corecraft.pack_api import generate_pack
from corecraft.pack_niches import FAMILY_OF, HI_KEYS, MENUS, PRICES
from corecraft.pack_types import TYPES

ROOT = Path(__file__).parent
NICHES = W.niches()
PACKS = {n: W.build_pack(v) for n, v in NICHES.items()}
TYPE_PACKS = W.build_type_packs()
FOODS = set(MENUS) | {"type_food_dining"}


class Spec(unittest.TestCase):
    def test_the_spec_was_read_completely(self):
        self.assertEqual((len(W.spec()["niches"]), len(W.spec()["types"])), (99, 20))
        self.assertTrue(all(len(n["services"]) == 6 and len(n["requests"]) == 6 for n in W.spec()["niches"]))
        self.assertEqual(len({n["id"] for n in W.spec()["niches"]}), 99)

    def test_every_niche_has_its_hand_written_layer(self):
        for nid in NICHES:
            self.assertIn(nid, FAMILY_OF, nid)
            self.assertIn(nid, PRICES, nid)
            self.assertEqual(len(HI_KEYS[nid]), 2, nid)
            self.assertEqual(len(PRICES[nid]), 3, nid)
        self.assertEqual(set(TYPES), {t["theme"] for t in W.spec()["types"]})

    def test_food_niches_have_a_menu(self):
        for nid in ("cafe_coffee_tea", "restaurant_dining", "bakery_cakes", "german_cafe", "chai_tea_stall"):   # the five the spec names
            self.assertIn(nid, MENUS)
            self.assertIn("menu", PACKS[nid])


class Packs(unittest.TestCase):
    def test_every_niche_pack_passes_the_spec_rules(self):
        for nid, p in PACKS.items():
            self.assertEqual(pack_check.check_pack(p, food=nid in MENUS), [], nid)

    def test_every_type_pack_passes_the_spec_rules(self):
        for p in TYPE_PACKS:
            self.assertEqual(pack_check.check_pack(p, food=p["id"] in FOODS), [], p["id"])

    def test_no_text_repeats_across_the_whole_batch(self):
        self.assertEqual(pack_check.check_batch(list(PACKS.values()) + TYPE_PACKS, foods=FOODS), [])

    def test_counts_and_shape(self):
        p = PACKS["pest_control"]
        self.assertEqual([len(p[k]) for k in ("heroTitles", "heroSubtitles", "features", "stats", "faq", "testimonials", "marquee")], [3, 3, 6, 3, 5, 3, 8])
        self.assertEqual((len(p["steps"]["items"]), len(p["about"]["paragraphs"]), len(p["about"]["points"]), len(p["pricing"]["plans"]), len(p["gallery"]["captions"]),
                          len(p["team"]["roles"]), len(p["blog"]["posts"])), (4, 2, 3, 3, 6, 3, 3))
        self.assertTrue(6 <= len(p["keywords"]) <= 14)
        self.assertEqual(p["cta"]["button"], p["button"])
        self.assertTrue(p["cta"]["title"].endswith("?"))

    def test_the_services_of_the_spec_are_the_features(self):
        for nid, n in NICHES.items():
            self.assertEqual([f["title"] for f in PACKS[nid]["features"]], [s if len(s) <= 30 else s[:30].rsplit(" ", 1)[0] for s in n["services"]], nid)

    def test_a_pest_control_page_never_talks_about_leaks_or_wiring(self):
        blob = json.dumps(PACKS["pest_control"]).lower()
        for w in ("leak", "wiring", "pipe", "bake", "menu"):
            self.assertNotIn(w, blob)

    def test_no_invented_claims(self):
        for nid, p in PACKS.items():
            blob = json.dumps(p).lower()
            for rx in (r"award", r"guarantee", r"100%", r"#1", r"best in", r"years of", r"customers served", r"\bcure[sd]?\b"):
                self.assertIsNone(re.search(rx, blob), (nid, rx))

    def test_prices_are_plain_usd_strings_that_do_not_fall(self):
        for nid, p in PACKS.items():
            prices = [float(x["price"][1:]) for x in p["pricing"]["plans"]]
            self.assertEqual(prices, sorted(prices), nid)
            self.assertTrue(all(x["price"].startswith("$") for x in p["pricing"]["plans"]), nid)

    def test_a_menu_has_no_prices(self):
        for nid in MENUS:
            for cat in PACKS[nid]["menu"]["categories"]:
                self.assertTrue(5 <= len(cat["items"]) <= 6, (nid, cat["name"]))
                self.assertFalse([i for i in cat["items"] if "$" in i or "rs " in i.lower()], nid)

    def test_the_city_goes_into_the_hero_subtitle_once(self):
        p = W.build_pack(NICHES["dental_clinic"], city="Jaipur")
        self.assertEqual(sum("Jaipur" in s for s in p["heroSubtitles"]), 3)
        self.assertNotIn("Jaipur", p["contactText"])
        self.assertEqual(pack_check.check_pack(p), [])

    def test_the_checker_catches_what_the_spec_forbids(self):
        bad = json.loads(json.dumps(PACKS["pest_control"]))
        bad["features"][0]["text"] = "Over 500+ customers trust our award-winning team and we guarantee results every time you call us!"
        bad["heroTitles"][0] = "lower case title"
        bad["pricing"]["plans"][0]["price"] = "free"
        problems = " ".join(pack_check.check_pack(bad))
        for needle in ("forbids", "exclamation", "Title Case", "plain USD"):
            self.assertIn(needle, problems)


class Requests(unittest.TestCase):
    def test_the_six_ways_of_asking_in_the_spec(self):
        for nid, n in list(NICHES.items())[:25]:
            x, x2, y, z, x5, x6 = n["requests"]
            for r in ("%s website" % x, "Create a website for a %s in Jaipur" % x2, "mujhe %s ki website banakar do" % y,
                      "meri %s ki dukaan ke liye website banao, with online contact and WhatsApp" % z, "modern %s website with animation, premium colours and a gallery" % x5,
                      "%s landing page, short, with pricing and FAQ" % x6):
                self.assertEqual(pack_request.understand(r)["niche"], nid, r)

    def test_all_requests_of_the_spec_are_understood(self):
        wrong = []
        for nid, n in NICHES.items():
            x, x2, y, z, x5, x6 = n["requests"]
            for r in ("%s website" % x, "Create a website for a %s in Jaipur" % x2, "mujhe %s ki website banakar do" % y, "meri %s ki dukaan ke liye website banao, with online contact and WhatsApp" % z):
                if pack_request.understand(r)["niche"] != nid:
                    wrong.append(r)
        self.assertEqual(wrong, [])

    def test_hold_out_keeps_most_of_the_accuracy(self):
        drop, reqs = {}, []
        for nid, n in NICHES.items():
            x, x2, y, z, x5, x6 = n["requests"]
            d = drop.setdefault(nid, set())
            d.update(pack_request._norm(w) for w in n["requests"])
            reqs += [("mujhe %s ki website banakar do" % y, nid), ("meri %s ki dukaan ke liye website banao, with online contact and WhatsApp" % z, nid)]
        pack_request.rebuild(drop)
        try:
            ok = sum(pack_request.understand(r, drop=drop)["niche"] == nid for r, nid in reqs)
        finally:
            pack_request.rebuild()
        self.assertGreaterEqual(ok / len(reqs), 0.9)

    def test_a_business_type_request_gets_the_type_pack(self):
        for t in W.spec()["types"]:
            out = generate_pack("Create a modern website for %s" % t["type_text"])
            self.assertEqual((out["source"], out["understood"]["type_theme"]), ("business-type pack", t["theme"]))

    def test_vague_requests_get_the_general_pack_and_say_so(self):
        for r in ("unique website", "business website", "I want a website", "something modern with animation"):
            out = generate_pack(r)
            self.assertEqual(out["understood"]["type_theme"], "general_business", r)
            self.assertTrue([n for n in out["notes"] if "does not name a trade" in n], r)

    def test_typos(self):
        for r, nid in (("pest controll website", "pest_control"), ("tatoo studio website", "tattoo_studio"), ("Create a website for a plumbar in Pune", "plumber_electrician"),
                       ("dental clinc website", "dental_clinic"), ("mujhe termite treatmnt ki website banakar do", "pest_control")):
            self.assertEqual(pack_request.understand(r)["niche"], nid, r)

    def test_fresh_requests(self):
        for r, nid in (("I need a website for my chai tapri in Pune", "chai_tea_stall"), ("yoga teacher training in Rishikesh website", "yoga_retreat"), ("mujhe gym ki website banani hai", "gym_fitness_studio"),
                       ("CA firm website for GST and ITR filing", "chartered_accountant"), ("NGO for stray dogs website", "animal_welfare"), ("scrap dealer website", "scrap_recycling")):
            self.assertEqual(pack_request.understand(r)["niche"], nid, r)

    def test_brand_and_city_are_read(self):
        out = generate_pack("Create a website for a bakery called Sweet Crumbs in Pune")
        self.assertEqual((out["understood"]["niche"], out["understood"]["brand"], out["understood"]["city"]), ("bakery_cakes", "Sweet Crumbs", "Pune"))
        self.assertEqual(out["problems"], [])
        blob = json.dumps(out["pack"])
        self.assertIn("Sweet Crumbs", blob)
        self.assertNotIn("{brand}", blob)
        self.assertIn("menu", out["pack"])

    def test_without_a_brand_the_placeholder_stays(self):
        self.assertIn("{brand}", json.dumps(generate_pack("pest control website")["pack"]))

    def test_hindi_is_flagged_not_faked(self):
        out = generate_pack("मुझे दीमक का इलाज की वेबसाइट चाहिए")
        self.assertEqual(out["understood"]["niche"], "pest_control")
        self.assertTrue([n for n in out["notes"] if "Devanagari" in n])

    def test_empty_request(self):
        with self.assertRaises(ValueError):
            generate_pack("  ")


class Site(unittest.TestCase):
    def test_a_site_from_a_request(self):
        from corecraft import pipeline
        with tempfile.TemporaryDirectory() as d:
            r = pipeline.run_pack("Create a website for a pest control in Jaipur", d, 1)
            page = (Path(r["dir"]) / "preview.html").read_text(encoding="utf-8")
            self.assertIn("Pest Control", page)
            self.assertNotIn("{brand}", page)
            self.assertNotIn("Sample Customer", page)
            self.assertTrue((Path(r["dir"]) / "pack.json").exists())

    def test_cli_prints_a_pack(self):
        r = subprocess.run([sys.executable, str(ROOT / "main.py"), "--pack", "mujhe termite treatment ki website banakar do"], capture_output=True, text=True, stdin=subprocess.DEVNULL, cwd=tempfile.gettempdir())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["id"], "pest_control")


class Production(unittest.TestCase):
    """What must hold when the pack path is used by other programs and by many people at once."""

    def test_every_niche_with_every_kind_of_city(self):
        cities = (None, "Pune", "Ahmedabad", "Thiruvananthapuram", "Visakhapatnam", "Sri Ganganagar", "Navi Mumbai Thane", "Bhubaneswar Odisha India")
        for nid, n in NICHES.items():
            for c in cities:
                p = W.build_pack(n, city=c)
                self.assertEqual(pack_check.check_pack(p, food=nid in MENUS), [], (nid, c))
                if c:
                    self.assertIn(c, json.dumps(p), (nid, c))
        for t in W.spec()["types"]:
            for c in cities:
                self.assertEqual(pack_check.check_pack(W.build_type_pack(t["theme"], c), food=t["theme"] == "food_dining"), [], (t["theme"], c))

    def test_names_and_cities_from_a_request_are_cleaned(self):
        for r in ('pest control called "{brand}"', "pest control called <b>Bad</b> in <i>Jaipur</i>", 'dental clinic called https://evil.example', "Create a website for a plumber in 12345",
                  "bakery called {{x}} ${y}", "Create a website for a bakery called A\"B in Delhi"):
            out = generate_pack(r)
            blob = json.dumps(out["pack"])
            for bad in ("<b>", "<i>", "http", "${", "{{"):
                self.assertNotIn(bad, blob, r)
            self.assertEqual(out["problems"], [], r)
        self.assertEqual(pack_request.clean_name("Sharma Brothers And"), "Sharma Brothers")
        self.assertIsNone(pack_request.clean_name("<b>x</b>"))
        self.assertIsNone(pack_request.clean_name("a" * 80))
        self.assertIsNone(pack_request.clean_name("Pune 411001", "city"))

    def test_hostile_requests_never_crash(self):
        for r in ("x" * 5000, "😀😀😀", "\x00\x01 pest control \u202e", "a " * 3000, "website\n\nfor\npest\ncontrol", "'; DROP TABLE users;--", "123456", "called \\ pest control"):
            out = generate_pack(r)
            self.assertEqual(out["problems"], [], r[:20])
        for bad in (None, 5, ["x"], "", "   "):
            with self.assertRaises(ValueError):
                generate_pack(bad)

    def test_same_request_same_pack(self):
        r = "Create a website for a bakery called Sweet Crumbs in Pune"
        self.assertEqual(generate_pack(r), generate_pack(r))

    def test_many_threads_get_the_same_answers(self):
        import threading
        want = {r: generate_pack(r)["pack"] for r in ("pest control website", "mujhe gym ki website banani hai", "Create a website for a bakery in Pune")}
        pack_request.rebuild()   # the next callers build the index at the same moment
        errors = []

        def work():
            try:
                for _ in range(20):
                    for r, p in want.items():
                        if generate_pack(r)["pack"] != p:
                            errors.append(r)
            except Exception as e:   # noqa: BLE001
                errors.append(repr(e))
        threads = [threading.Thread(target=work) for _ in range(12)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(errors, [])

    def test_a_pack_that_fails_the_checker_is_never_handed_out(self):
        from corecraft import pack_api
        real = pack_check.check_pack
        pack_check.check_pack = lambda *a, **k: ["forced problem"]
        try:
            with self.assertRaises(pack_api.PackError):
                generate_pack("pest control website")
        finally:
            pack_check.check_pack = real

    def test_the_checker_runs_on_the_placeholder_not_on_the_name(self):
        out = generate_pack("Create a website for a pest control called Sharma Brothers Pest Control Services in Thiruvananthapuram")
        self.assertEqual(out["problems"], [])
        self.assertIn("Sharma Brothers Pest Control Services", out["pack"]["about"]["paragraphs"][0])

    def test_pictures_failing_do_not_break_the_site(self):
        from corecraft import photo_engine, pipeline
        real = photo_engine.generate_photos

        def boom(*a, **k):
            raise RuntimeError("image engine down")
        photo_engine.generate_photos = boom
        try:
            with tempfile.TemporaryDirectory() as d:
                r = pipeline.run_pack("pest control website in Jaipur", d, 1, photos=True)
                self.assertTrue((Path(r["dir"]) / "preview.html").exists())
                self.assertTrue([n for n in r["needs_review"] if "pictures could not be made" in n])
        finally:
            photo_engine.generate_photos = real

    def test_cli_errors_are_one_clear_line(self):
        def run(*a):
            return subprocess.run([sys.executable, str(ROOT / "main.py"), *a], capture_output=True, text=True, stdin=subprocess.DEVNULL, cwd=tempfile.gettempdir())
        r = run("--pack", "pest control", "--out", "/proc/nope/x.json")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("cannot write", r.stderr)
        with tempfile.TemporaryDirectory() as d:
            r = run("--pack", "pest control website", "--out", d + "/p/pest.json")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(Path(d + "/p/pest.json").read_text())["id"], "pest_control")


if __name__ == "__main__":
    unittest.main()
