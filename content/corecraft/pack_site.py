"""A niche pack as a website: pack (spec shape) -> the content dict the site generator reads. The pack's sample testimonials and its team roles are left out of the page
(they are not real people), prices are shown as sample prices in rupees (USD x 80, as the spec says), and the page says what is still to be filled in."""
import json
import re

from .content_engine import UI_EN
from .pack_niches import FAMILY_OF
from .pack_writer import FAMILIES

KIND = {"home": "home", "auto": "trades", "project": "creative", "retail": "retail", "food": "food", "clinic": "health", "session": "beauty", "pro": "pro", "edu": "education",
        "events": "events", "stay": "travel", "property": "pro", "nonprofit": "org", "software": "software"}
MOOD = {"modern_tech": "cool", "organic_nature": "calm", "luxury_minimal": "elegant", "playful_vibrant": "playful", "bold_fitness": "bold", "professional_services": "cool", "healthcare": "calm",
        "food_dining": "warm", "education": "friendly", "creative_studio": "elegant", "general_business": "friendly", "real_estate": "elegant", "travel_tourism": "warm", "automotive": "bold",
        "beauty_wellness": "elegant", "events_wedding": "elegant", "pets_animals": "friendly", "fashion_retail": "elegant", "home_services": "friendly", "nonprofit": "warm"}


def _rupees(price, period):
    v = float(price.lstrip("$")) * 80
    amount = "Free" if v == 0 else "Rs {:,.0f}".format(v) if v >= 10 else "Rs {:.0f}".format(v)
    return ("%s %s" % (amount, period)).strip() if v else "Free %s" % period.lstrip("/")


def content_from_pack(pack, brand=None, city=None):
    invented = not brand
    label = pack["label"]
    if invented:
        brand = label + (", " + city if city else "")
    text = json.dumps(pack, ensure_ascii=False).replace("{brand}", brand.replace('"', "'"))
    p = json.loads(text)
    fam = FAMILY_OF.get(p["id"]) or "home"
    ui = dict(UI_EN)
    stats = [{"value": s["value"], "label": s["label"]} for s in p["stats"]]
    highlights = [{"title": pt, "text": "%s: %s." % (stats[i]["value"], stats[i]["label"])} for i, pt in enumerate(p["about"]["points"])]
    blog = [{"title": b["title"], "excerpt": "%s notes for people looking into %s." % (b["tag"], label.lower())} for b in p["blog"]["posts"]]
    pricing = [{"name": pl["name"], "price": _rupees(pl["price"], pl["period"])} for pl in p["pricing"]["plans"]]
    content = {
        "brand": brand, "niche": p["id"], "kind": KIND.get(fam, "pro"), "profile": "", "business_type": p["id"], "type_label": label, "lang": "en", "ui": ui, "mood": MOOD.get(p["theme"], "friendly"),
        "keywords": [k for k in p["keywords"] if k.isascii()][:6], "eyebrow": label + (" · " + city if city else ""), "location": city or "", "audience": "",
        "hero_heading": p["heroTitles"][0], "tagline": p["heroSubtitles"][0], "about_title": ui["about_us"] if invented else ui["about_title"] % brand, "about": p["about"]["paragraphs"],
        "features_title": p["featureTitle"], "features": p["features"], "highlights": highlights, "stats_title": "At a glance", "stats": stats,
        "steps_title": p["steps"]["title"], "steps": p["steps"]["items"], "faq_title": "Good questions", "faq": p["faq"], "blog_title": p["blog"]["title"], "blog": blog,
        "contact": {"place": city} if city else {}, "cta_primary": p["button"], "cta_secondary": ui["faq"], "cta_text": p["contactText"], "cta_title": p["cta"]["title"],
        "footer": "© %s. %s" % (brand, ui["rights"]), "offers": [], "hours": "", "prices": [], "pricing": pricing, "facts_used": {}, "missing": ["name" if invented else None, "phone", "email", "address", "hours"],
        "generated_by": {"business_type": "%s (niche pack)" % p["id"], "items_from_prompt": [f["title"] for f in p["features"]], "place": city or "", "mode": "niche pack", "copy": "pack text from the training spec"},
        "needs_review": ["This page uses the %s niche pack. Replace the sample prices (USD x 80) and add your real phone, address and hours before publishing." % p["id"]]
        + (["No business name was given, so the heading is '%s' (not a name)." % brand] if invented else []),
    }
    content["missing"] = [m for m in content["missing"] if m]
    if "menu" in p:
        content["menu"] = p["menu"]
    return content
