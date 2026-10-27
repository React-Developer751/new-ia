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

## What it promises

- Uses only facts you gave (name, city, services, offers, hours, prices, phone, address). Nothing is invented; what is missing is listed in `missing`.
- Every page passes validators: no placeholders, no repeated 6-word span, no other niche's words, every named service present.
- Same prompt + same seed gives the same page. Input is cleaned (markup, braces, newlines, very long text) and bad `--facts` files give a clear error.
- `needs_review` tells you when to check: invented brand name, unsure business type, typical offerings used, no city.

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

Retraining (optional, needs internet only for `fetch_*`): `training/train.py`, `training/train_templates.py`. Data lives in `data/`.
