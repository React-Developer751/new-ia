# Core-Craft AI

One short description of a business (English, Hinglish or Hindi) in, a React static website out.
Pure Python standard library: no pip, no external AI, no API, no internet at run time.

## Use

```bash
python3 main.py "Italian restaurant Forno Rosso, Mumbai, wood fired pizza, fresh pasta, tiramisu, open 12pm to 11pm, online booking"
python3 main.py "mujhe ek dental clinic chahiye Pune mein, braces, implants" --out sites --seed 1
python3 main.py "bakery in Delhi" --facts my_facts.json
```

Output (in `output/<brand>/`): `preview.html` (open directly), `App.jsx` + `index.html` + `styles.css` (React; `index.html` loads React from a CDN in the browser),
`content.json`, `palette.json`, generated images/assets.

`--facts` is a JSON object: `name, city, services[], phone, email, address, hours[], prices[{name,price}], testimonials[{name,text}], team[{name,role}], whatsapp, years, tagline`.
Anything in it wins over what is read from the prompt. As a library: `from corecraft.content_engine import generate_content`.

## Web UI (check and train)

```bash
python3 webui.py        # then open http://127.0.0.1:8765  (this computer only)
```

- **Generate & check**: type a prompt (optionally real details), see the page preview and a report: type + confidence, city, hours, services read, offers, what is missing, review notes.
- **Wrong type?** Pick the right one and save it as a training example (`data/feedback.json`).
- **Train** tab: retrains the detector on the shipped labels plus your corrections (about 15 s, offline). The new model is kept only if its score on the held-out prompts does not drop; otherwise the old one is restored.

Training teaches business-type detection only. Wording comes from the hand-written frames in `corecraft/voice_*.py`.

## Niche content packs (the "Content AI training prompts" spec)

The training PDF asks for the text of 99 niches and 20 business types in one JSON shape (hero titles, 6 features, steps, FAQ, pricing, gallery, team, testimonials, blog, marquee,
and a menu for food). The engine now writes exactly that, from a plain request.

```bash
python3 main.py --pack "Create a website for a pest control in Jaipur"           # prints the pack (JSON)
python3 main.py --pack "mujhe termite treatment ki website banakar do" --out packs/pest.json
python3 main.py --pack-site "Create a website for a bakery called Sweet Crumbs in Pune" --out sites   # pack -> website
python3 training/export_packs.py            # output/niche_packs/batch-1..10.json (99 niches) + type-packs.json (20 types), checked
python3 training/eval_requests.py --fresh   # how well requests are understood
python3 webui.py                            # "Content pack" tab
```

- `corecraft/pack_request.py` reads the request (English, Hinglish, typos) and finds the niche; `pack_writer.py` writes the pack from the niche's six services plus hand-written text banks
  (`pack_families_*.py`); `pack_check.py` is the spec's rules as code (counts, lengths, Title Case, no emoji or "!", no invented numbers, awards or ratings, no repeated text, USD prices).
- Prices in a pack are sample figures (USD, the generator converts them); testimonials are generic samples. A named business replaces `{brand}`; a named city goes once into the hero subtitles.
- A pack is checked by the spec checker before it is returned (`PackError` if it ever fails: that would be a bug, never bad input). Names and cities from a request are cleaned (no markup, braces, links);
  a city too long for the subtitle rules moves to the contact text. `--pack-site` uses the image engine when it is installed and falls back to the built-in artwork when it is not.
- Not built: Hindi (Devanagari) packs. A Hindi request is understood, but the pack comes back in English with a note.
- Data: `data/niche_spec.json` (read from the PDF by `training/import_niches.py`), the hand-written layer is `corecraft/pack_niches.py`.

## What it promises

- Uses only facts you gave (name, city, services, offers, hours, prices, phone, address). Nothing is invented; what is missing is listed in `missing`.
- Every page passes validators: no placeholders, no repeated 6-word span, no other niche's words, every named service present.
- Same prompt + same seed gives the same page. Input is cleaned (markup, braces, newlines, very long text) and bad `--facts` files give a clear error.
- `needs_review` tells you when to check: invented brand name, unsure business type, typical offerings used, no city.
- No business name given: the heading says what the business is and where ("Dental Clinic, Pune"). Nothing is made up; `needs_review` says to add your name (and suggests one from a business email domain, never uses it).
- Typos: words that name the kind of business ("resturant", "salun", "gim") are corrected everywhere; inside the detected trade a one-letter slip in an unknown word ("makup", "cardeo") is corrected too. Real names and dishes are left alone, and every change is listed in `needs_review`.
- Services typed with no commas ("dog food cat food aquarium fish toys") are cut with known phrases and word shape. On 16 fresh prompts I did not tune on, 66% of services came out right (3% without it), and the page always notes how the run was cut so you can add commas.
- Whole sentences work too ("We are a bakery in Jaipur. We make cakes and cookies. You can order on WhatsApp.").

## Limits (read these)

- 77 business types, 23 sub-niches (cuisines, dental/skin/eye, yoga/gym ...). An unlisted type gets neutral copy and a `needs_review` note.
- Copy comes from hand-written frames filled with your words. It reads well, but it is not a human copywriter: give 3+ real services for the best page.
- Business-type detection scored 97% on the author's own hold-out set; it has not been measured on outside traffic. Low confidence is flagged, not hidden.
- Hindi pages use Hindi frames only; Hinglish is read, and written as English.
- No prices, reviews or team are shown unless you supply them.

## Checks

```bash
python3 -m unittest discover -p "test_*.py"   # 100+ tests
python3 training/evaluate.py                  # accuracy / quality numbers
python3 training/check_copy.py                # no 6-word span copied from training pages
```

Typo vocabulary: `python3 training/build_vocab.py` rebuilds `data/vocab.json`.

Retraining (optional, needs internet only for `fetch_*`): `training/train.py`, `training/train_templates.py`. Data lives in `data/`.
