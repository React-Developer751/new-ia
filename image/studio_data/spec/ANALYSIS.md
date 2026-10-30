# Analysis of Image-AI-training.pdf (62 pages)

## What it is
The training spec for the image AI ("PixelMath") of a website generator: how every website asks for its pictures.

1. **System prompt**: one clear subject, calm space for a headline, no text / letters / numbers / logos / watermarks / real brands, no recognisable real people (simple
   illustrated characters, side or back view when possible), one drawing style, one lighting, one palette for all pictures of a site.
2. **STYLE LINE** added to every request: "friendly flat illustration, clean vector shapes, soft shading, one clear subject, rich but harmonious colours, no text ...".
3. **25 design styles** (minimal, cyberpunk, glass, luxe dark, trust navy, ...): page styles that mean "light background, airy, soft shadows" (18) or "dark background, glowing
   accents, deep shadows" (7).
4. **99 businesses x 20 pictures = 1980 prompts**: hero-1..3 (1600x900, subject right or centre, empty left), about (1200x900), gallery-1..6 (900x900), card-1..6 (800x600,
   service name + one-line description), team-1..3 (600x600, "portrait of a friendly <role>, illustrated character, shoulders up"), background (1600x900, "soft abstract
   background texture in the mood of <business>, no subject"). 95 businesses have two palettes, 4 have one (accent + background hex, named: Trades, Workwear, Chambers ...).
5. **20 generic business types x 10 pictures = 200 prompts** (hero x3, about, gallery x6) for businesses without a pack of their own.
Every prompt ends with ", for a <business name in lower case> website" (all 2180 verified).

## Findings
* **Business coverage.** 73 of the 99 businesses already had a picture niche in the studio; 26 had none (pest control, laundry, water purifier, car rental, gift shop, diagnostic lab,
  counselling, notary, DJ, video editing, funeral, scrap, farm stay, PG hostel, temple, nutritionist, animal welfare, chai stall, cloud kitchen, tiffin, mobile repair, bike garage,
  bridal makeup, drone, banquet hall, loan agent). Several others were approximate (school vs preschool, plumber and electrician share one business).
* **The subject text alone does not identify the business.** 212 of 297 hero prompts share no word with the business name ("shield and house" for pest control,
  "sea at dusk with a moon" for funeral services, "futuristic cyberpunk city at night" for a SaaS startup); 85 subject strings are reused by several businesses ("chef in a
  kitchen" x7). Only the 594 gallery prompts carry the business in brackets ("Termite drilling (pest control)"). So the business named in "for a <business> website" must
  decide the scene, and the subject can only steer it (this is how `pixelmath/studio/spec.py` works).
* **Baseline before this work:** matching the 1460 prompts of the 73 covered businesses by their text: 77.9% right niche, 14.9% refused, 7.2% wrong (worst: school vs playschool,
  digital agency vs mobile app, sports academy vs gym, plumber vs electrician).
* **Picture counts per business are fixed (16 scene pictures + 3 portraits + 1 texture)** from one scene, so scene pictures must differ by camera / crop, not by object.
* **Rules the old studio broke:** scenes drew letters and numbers ("STOP", "40", "TAXI", "GAME ON", "FRESH BREAD", ...), against "no text, letters, numbers or logos".
* **Things the spec leaves open** (decided in the implementation): what a team portrait of each role wears, which styles map to dark / light, what to do with a style the engine cannot
  draw (photo-like, 3D, sketch: the flat illustration is used and the report says so), and the picture of a business with no pack (`a general local business` -> neutral abstract).

## What was built from it
26 new niches (123 in total), the spec parser and renderer (`pixelmath/studio/spec.py`), the portrait renderer, the background texture, the no-text rule, the classifier training from
the spec's captions (1618 train / 552 held out), the `/spec` API, and a full render of all 2180 pictures (`samples/spec_run/`, checked by `examples/spec_check.py`).
