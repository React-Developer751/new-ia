"""Niche packs: the text of ONE kind of business in the shape the "Content AI" spec asks for (heroTitles, features, steps, faq, pricing, menu ...).
build_pack(niche) -> dict in the spec's shape, with the literal {brand} placeholder. render_pack(pack, brand, city) fills the placeholder for a page.
Everything is written from the niche's own services (from data/niche_spec.json) and the hand-written text banks in pack_families_*.py. No numbers of customers, years,
ratings or awards are ever written; pack_check.py enforces that."""
import json
import re
import zlib
from pathlib import Path

from . import pack_families_a as FA
from . import pack_families_b as FB
from .pack_niches import BUTTON, FAMILY_OF, HI_KEYS, MENUS, PRICES, TEAM

SPEC_PATH = Path(__file__).resolve().parent.parent / "data" / "niche_spec.json"
FAMILIES = {"home": FA.HOME, "auto": FA.AUTO, "project": FA.PROJECT, "retail": FA.RETAIL, "food": FA.FOOD, "food_order": FA.FOOD_ORDER, "clinic": FA.CLINIC, "session": FA.SESSION,
            "pro": FB.PRO, "edu": FB.EDU, "events": FB.EVENTS, "stay": FB.STAY, "property": FB.PROPERTY, "nonprofit": FB.NONPROFIT, "software": FB.SOFTWARE}
_cache = {}
FAQ_TAILS = ["This applies to {s1}, {s2} and the rest of our {l} work.", "It is the same for {s2} as it is for {s1}.", "That goes for {s3} and {s4} too.",
             "Ask us about {s5} or {s6} and the answer is the same.", "The same approach applies to {s1} and {s6}."]
HERO_FALLBACK = ["{L} Made Simple And Clear", "Your Local {L} Team Nearby", "Friendly {L} Help Without The Fuss", "Clear {L} Help When You Need It"]
SUB_FALLBACK = ["{brand} offers {s1} and {s2}. Tell us what you need and we will reply with a clear plan and a fair price{city_in}.",
                "Looking for {l}? {brand} listens first, explains the options in plain words and keeps you informed{city_in}.",
                "{brand} is here for {s1} and {s3}. Ask us anything and we will answer simply and without pressure{city_in}."]


def spec():
    if "s" not in _cache:
        _cache["s"] = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    return _cache["s"]


def niches():
    return {n["id"]: n for n in spec()["niches"]}


def tc(s):
    """Title Case the way the spec does it: every word starts with a capital (even "And" and "A")."""
    return " ".join(w[:1].upper() + w[1:] if w[:1].isalpha() else w for w in s.split())


def low(s):
    """Lower case, but keep acronyms and names with inner capitals (AC, CCTV, SUVs, iPhone). "Single-Use" is two plain words, so it goes lower case."""
    out = []
    for w in s.split():
        parts = []
        for part in w.split("-"):
            core = re.sub(r"[^A-Za-z]", "", part)
            parts.append(part if len(core) > 1 and (core.isupper() or re.search(r"[a-z][A-Z]", core)) else part.lower())
        out.append("-".join(parts))
    return " ".join(out)


def _h(*parts):
    return zlib.crc32("|".join(str(p) for p in parts).encode("utf-8"))


def _rotate(items, key):
    if not items:
        return []
    k = _h(key) % len(items)
    return items[k:] + items[:k]


def _fmt(pattern, tok):
    return pattern.format(**tok)


def _pick(patterns, tok, ok, key, used=()):
    """The first pattern (in a niche specific order) whose result passes ok() and was not used yet."""
    for p in _rotate(patterns, key):
        t = _fmt(p, tok)
        if ok(t) and t not in used:
            return t
    raise ValueError("no pattern fits %r for %s" % (patterns[:2], key))


def _tokens(label, services, city=None):
    tok = {"L": tc(label), "l": low(label), "city_in": (" in %s" % city) if city else "", "brand": "{brand}"}
    for i, s in enumerate(services, 1):
        tok["S%d" % i] = tc(s)
        tok["s%d" % i] = low(s)
    return tok


JOINERS = {"and", "for", "of", "with", "in", "on", "at", "to", "a", "an", "the", "or"}


def _short_service(s):
    w = [x.rstrip(",") for x in s.split()]
    for cand in (s, " ".join(w[:2]), " ".join(w[-2:]), w[0], w[-1]):
        c = cand.split()
        if len(cand) <= 16 and len(c) <= 2 and c[0].lower() not in JOINERS and c[-1].lower() not in JOINERS:
            return cand
    return w[0][:16]


def _caption(s):
    w = s.replace(",", "").split()
    if len(w) > 4:
        w = w[:4]
    if len(w) < 2:
        w = w + ["Work"]
    return " ".join(w)


def _price(v):
    return "$%d" % v if float(v).is_integer() else "$%.2f" % v


def _keywords(n):
    if n.get("_keywords_only"):
        return list(n["keywords"])[:14]
    kws, seen = [], set()
    generic = {"services", "service", "shop", "company", "store", "studio", "agency", "centre", "center", "clinic", "tapri"}
    for k in n["keywords"] + HI_KEYS.get(n["id"], []):
        k = k.strip().lower()
        if not k or k in seen or k in generic:
            continue
        seen.add(k)
        kws.append(k)
    latin = [k for k in kws if k.isascii()][:12]
    deva = [k for k in kws if not k.isascii()][:2]
    return (latin + deva)[:14]


def build_pack(niche, city=None):
    nid = niche["id"]
    fam = FAMILIES[niche.get("_family") or FAMILY_OF[nid]]
    label = niche["label"]
    services = list(niche["services"])
    tok = _tokens(label, services, city)
    key = nid
    rot = _h(nid)
    L = tok["L"]

    def title_ok(lo, hi):
        return lambda t: lo <= len(t) <= hi
    hero = []
    hero_patterns = [p for p in fam["hero"] if "{S" not in p] if niche.get("_keywords_only") else fam["hero"]
    for p in _rotate(hero_patterns, key + "h") + HERO_FALLBACK:
        t = _fmt(p, tok)
        if 25 <= len(t) <= 58 and t not in hero:
            hero.append(t)
        if len(hero) == 3:
            break
    def _subtitles(tk):
        out = []
        for p in _rotate(fam["sub"], key + "s") + SUB_FALLBACK:
            t = _fmt(p, tk)
            if 80 <= len(t) <= 150 and t not in out:
                out.append(t)
            if len(out) == 3:
                break
        return out
    subs = _subtitles(tok)
    city_in_contact = False
    if len(subs) < 3 and city:   # a long city name pushes the subtitles over 150 characters: say the city once, in the contact text, as the spec allows
        subs = _subtitles(dict(tok, city_in=""))
        city_in_contact = True
    features = []
    frames = fam["feat"]
    used_text = set()
    for i, s in enumerate(services):
        title = s if len(s) <= 30 else s[:30].rsplit(" ", 1)[0]
        done = None
        for j in range(len(frames)):
            t = frames[(rot + i + j) % len(frames)].format(s=low(s), S=tc(s), L=L, l=tok["l"])
            if 50 <= len(t) <= 115 and t not in used_text:
                done = t
                break
        if done is None:
            raise ValueError("%s: no feature text fits %r" % (nid, s))
        used_text.add(done)
        features.append({"title": title, "text": done})
    stats = [{"value": v, "label": l} for v, l in _rotate(fam["stats"], key + "t")[0]]
    steps_title = _pick(fam["steps_title"], tok, lambda t: True, key + "st")
    steps = [{"title": t, "text": _fmt(x, tok)} for t, x in fam["steps"]]
    faq_pool = _rotate(fam["faq"], key + "q")[:5]
    faq = []
    tails = _rotate(FAQ_TAILS, key + "ft")
    for i, (q, ans) in enumerate(faq_pool):
        ans = _fmt(ans, tok)
        if not any(w in ans.lower() for w in [tok["l"]] + [tok["s%d" % k] for k in range(1, 7)]):
            ans = ans + " " + _fmt(tails[i % len(tails)], tok)   # the same answer must not appear on the page of another niche
        faq.append({"q": _fmt(q, tok), "a": ans})
    button = niche.get("_button") or BUTTON.get(nid) or fam["button"]
    cta_patterns = [p for p in fam["cta_title"] if "{S" not in p] or ["Ready To Get Started With {L}?"] if niche.get("_keywords_only") else fam["cta_title"]
    cta_title = _pick(cta_patterns, tok, lambda t: len(t) <= 60, key + "c")
    about_title = _pick(fam["about_title"], tok, lambda t: True, key + "a")
    ab = _rotate(fam["about"][0], key + "p1")[0], _rotate(fam["about"][1], key + "p2")[0]
    price_rows = niche.get("_prices") or PRICES[nid]
    plans = []
    for (name, perks), (price, period) in zip(fam["plans"], price_rows):
        plans.append({"name": name, "price": _price(price), "period": period, "perks": [_fmt(x, tok) for x in perks]})
    captions = []
    for s in services:
        c = _caption(s)
        captions.append(c)
    if len(set(captions)) < 6:
        captions = [_caption(s) + ("" if i == 0 else "") for i, s in enumerate(services)]
    roles = niche.get("_team") or TEAM.get(nid) or [_fmt(r, tok) for r in fam["roles"]]
    tests = [{"quote": _fmt(q, tok), "role": r} for q, r in _rotate(fam["testimonials"], key + "x")[:3]]
    posts = [{"tag": t, "title": _fmt(p, tok)} for t, p in _rotate(fam["blog"], key + "b")[:3]]
    marquee, seen = [], set()
    for m in [_short_service(s) for s in services[:5]] + [tc(w) for w in fam["marquee_extra"]] + [_short_service(s) for s in services[5:]]:
        if m.lower() not in seen and len(m) <= 16 and len(m.split()) <= 2:
            seen.add(m.lower())
            marquee.append(m)
        if len(marquee) == 8:
            break
    for kw in niche["keywords"]:   # fewer than 8 short words so far: top up from the words people use
        m = tc(kw)
        if len(marquee) < 8 and m.isascii() and m.lower() not in seen and len(m) <= 16 and len(m.split()) <= 2:
            seen.add(m.lower())
            marquee.append(m)
    contact = _pick(fam["contact"], tok, lambda t: True, key + "k")
    if city_in_contact:
        contact = contact.rstrip(".") + " in %s." % city
    pack = {
        "id": nid, "label": label, "theme": niche["theme"], "keywords": _keywords(niche), "heroTitles": hero, "heroSubtitles": subs, "button": button,
        "featureTitle": _pick(fam["feature_title"], tok, title_ok(20, 60), key + "f"), "features": features, "stats": stats,
        "steps": {"title": steps_title, "items": steps}, "faq": faq, "cta": {"title": cta_title, "button": button},
        "about": {"title": about_title, "paragraphs": [_fmt(ab[0], tok), _fmt(ab[1], tok)], "points": list(_rotate(fam["points"], key + "pt")[0])},
        "pricing": {"title": _pick(fam["pricing_title"], tok, lambda t: True, key + "pr"), "plans": plans},
        "gallery": {"title": _pick(fam["gallery_title"], tok, lambda t: True, key + "g"), "captions": captions},
        "team": {"title": fam["team_title"], "roles": roles},
        "testimonials": tests, "blog": {"title": _pick(fam["blog_title"], tok, lambda t: True, key + "bt"), "posts": posts}, "marquee": marquee, "contactText": contact,
    }
    menu = niche.get("_menu") or MENUS.get(nid)
    if menu:
        title, lead, cats = menu
        pack["menu"] = {"title": title, "lead": lead, "categories": [{"name": n, "items": list(i)} for n, i in cats]}
    return pack


def build_type_pack(theme, city=None):
    """The general pack of one business type of the spec (theme is the spec's theme name)."""
    from .pack_types import TYPE_MENU, TYPES
    t = next(x for x in spec()["types"] if x["theme"] == theme)
    short, fam, items, kws, prices, button = TYPES[theme]
    niche = {"id": "type_" + theme, "label": short[:1].upper() + short[1:], "theme": theme, "services": items, "keywords": kws,
             "_family": fam, "_prices": prices, "_button": button, "_keywords_only": True, "_team": None}
    if theme == "food_dining":
        niche["_menu"] = TYPE_MENU
    p = build_pack(niche, city)
    p["label"] = t["type_text"][:1].upper() + t["type_text"][1:]
    return p


def build_type_packs():
    """The 20 general packs, one per business type of the spec."""
    return [build_type_pack(t["theme"]) for t in spec()["types"]]


def render_pack(pack, brand=None, city=None):
    """The pack with {brand} replaced (for a preview or a page). The city, when given and not already in the text, goes once into the contact text."""
    text = json.dumps(pack, ensure_ascii=False)
    if brand:
        text = text.replace("{brand}", brand.replace("\\", "").replace('"', "'"))
    out = json.loads(text)
    if city and city not in json.dumps(out, ensure_ascii=False):
        out["contactText"] = out["contactText"].rstrip(".") + " in %s." % city
    return out
