"""generate_pack(request): the whole path from what a person types to a niche pack in the shape of the training spec.
request -> (niche or business type, brand, city, language) -> pack -> checked by pack_check -> {"pack", "understood", "notes", "problems"}"""
import json

from . import pack_check, pack_request, pack_writer as W
from .pack_niches import MENUS

HINDI_NOTE = "The request is in Hindi. Hindi (Devanagari) packs are not built yet, so this pack is in English; the keys are the same."


def _fill_brand(pack, brand):
    text = json.dumps(pack, ensure_ascii=False).replace("{brand}", brand.replace("\\", "").replace('"', "'"))
    return json.loads(text)


class PackError(RuntimeError):
    """A pack that fails the spec's own checker is never handed out; this is raised instead (it means a bug, not bad input)."""


def _build(u, with_city, with_brand):
    city = u["city"] if with_city else None
    if u["niche"]:
        pack, food = W.build_pack(W.niches()[u["niche"]], city=city), u["niche"] in MENUS
    else:
        pack, food = W.build_type_pack(u["type_theme"], city=city), u["type_theme"] == "food_dining"
    problems = pack_check.check_pack(pack, food=food)   # checked with {brand} still in it: the spec counts the placeholder, not the name
    if with_brand and u["brand"] and not problems:
        pack = _fill_brand(pack, u["brand"])
        if u["brand"] not in pack["about"]["paragraphs"][0]:
            problems.append("brand missing from about.paragraphs[0]")
    return pack, problems


def generate_pack(request):
    if not isinstance(request, str):
        raise ValueError("request must be text")
    if not request.strip():
        raise ValueError("request is empty")
    u = pack_request.understand(request)
    notes = []
    for with_city, with_brand in ((True, True), (False, True), (True, False), (False, False)):
        pack, problems = _build(u, with_city, with_brand)
        if not problems:
            break
    else:
        raise PackError("could not build a pack that passes the spec checks for %r: %s" % (request[:60], "; ".join(problems[:3])))
    if u["city"] and not with_city:
        notes.append("The city %r was left out because it could not be placed without breaking the spec's length rules." % u["city"])
    if u["brand"] and not with_brand:
        notes.append("The business name %r was not used; {brand} stays in the text." % u["brand"])
    if u["niche"]:
        source = "niche pack"
    else:
        source = "business-type pack"
        if u.get("vague"):
            notes.append("The request does not name a trade, so this is the general local business pack: honest text that fits any neighbourhood business. Name the trade (e.g. 'pest control') for a specific pack.")
        else:
            notes.append("No niche pack matches this request exactly, so this is the general pack for businesses of this type.")
    if u["lang"] == "hi":
        notes.append(HINDI_NOTE)
    if u.get("typos"):
        notes.append("Corrected typing mistakes: %s." % ", ".join("'%s' to '%s'" % t for t in u["typos"]))
    if u["confidence"] < 0.15 and u["niche"]:
        notes.append("Several niches fit about equally well (%s); this is the closest." % ", ".join(n for _, n in u["scores"][:3]))
    return {"request": request, "source": source, "understood": {k: u[k] for k in ("niche", "type_theme", "brand", "city", "lang", "confidence")}, "notes": notes, "problems": problems, "pack": pack}
