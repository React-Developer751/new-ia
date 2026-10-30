"""Understand what a person types to ask for a website ("pest control website", "Create a website for a pest control in Jaipur", "mujhe termite treatment ki website banakar do",
"meri cockroach control ki dukaan ke liye website banao, with online contact and WhatsApp") and find the niche pack (or business-type pack) that answers it.
Stdlib only. The index is built from data/niche_spec.json: the niche's keywords (English, Hinglish, Devanagari), its label and its six services."""
import math
import re
import threading

from . import pack_writer as W
from .pack_niches import HI_KEYS
from .pack_types import TYPES

_cache = {}
_lock = threading.Lock()
FLUFF = ("create a modern website for", "create a website for", "make a website for", "build a website for", "i need a website for", "i want a website for", "looking for a website for",
         "with online contact and whatsapp", "with animation, premium colours and a gallery", "with animation", "premium colours", "and a gallery", "landing page, short, with pricing and faq",
         "short, with pricing and faq", "with pricing and faq", "banakar do", "banakar dijiye", "bana do", "banao", "banani hai", "banwani hai", "chahiye", "ke liye", "ki website", "ka website",
         "ki dukaan", "ki dukan", "ka dukaan", "meri", "mera", "mere", "mujhe", "humein", "hume", "hamari", "hamara", "की वेबसाइट", "का वेबसाइट", "वेबसाइट", "बनाओ", "बना दो", "बनाइए", "चाहिए",
         "मुझे", "मेरी", "मेरा", "मेरे", "के लिए")
STOP = set("""website site webpage page create make build design need want for a an the in at of to with and or my our me i we you your is are it this that online contact whatsapp whats app
modern animation premium colours colors colour gallery landing short pricing faq price prices please like some any new best good unique simple business company companies service services
shop store studio agency centre center near work help best""".split()) - {"design"}
STEM = re.compile(r"(?<=[a-z]{3})(?:ies|es|s)$")
CITY_RX = re.compile(r"\b(?:in|at|near|based in)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)|\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\s+(?:mein|me)\b")
BRAND_RX = re.compile(r"(?:called|named|name is|naam)\s+[\"']?([A-Z][\w&'-]*(?:\s+[A-Z][\w&'-]*){0,5})|[\"“]([^\"”]{2,40})[\"”]")
HINGLISH = re.compile(r"\b(mujhe|meri|mera|mere|banakar|banao|chahiye|dukaan|dukan|ki website|ke liye|hamara|humein|banani|hai)\b", re.I)


def _norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^\wऀ-ॿ' ]+", " ", s.lower())).strip()


def _tokens(s):
    out = []
    for t in _norm(s).split():
        if t in STOP or len(t) < 2:
            continue
        out.append(STEM.sub("", t) if t.isascii() else t)
    return out


def _index():
    if "i" in _cache:
        return _cache["i"]
    with _lock:   # the web UI answers on several threads: build the index once
        if "i" not in _cache:
            _cache["i"] = _build_index()
    return _cache["i"]


def clean_name(s, kind="brand"):
    """A business name or a city from a request is data: no markup, braces, backslashes or links, bounded length, and it has to contain letters."""
    s = " ".join(str(s).split()).strip(" .,;:-\"'")
    while s.split() and s.split()[-1].lower() in ("and", "of", "the", "&", "for", "in", "at", "pvt", "ltd"):
        s = " ".join(s.split()[:-1])   # a name cut off in the middle of a connector
    limit = 40 if kind == "brand" else 30
    if not (2 <= len(s) <= limit) or re.search(r"[{}<>\\`$@/=|]|https?:|www\.", s) or not re.search(r"[A-Za-z\u0900-\u097f]{2}", s):
        return None
    if kind == "city" and re.search(r"\d", s):
        return None
    return s


def _build_index():
    entries, df = [], {}
    for n in W.spec()["niches"]:
        kws = [k for k in n["keywords"]] + HI_KEYS.get(n["id"], [])
        phr = {}
        for k in kws:
            phr[_norm(k)] = max(phr.get(_norm(k), 0), 3.0)
        phr[_norm(n["label"])] = max(phr.get(_norm(n["label"]), 0), 3.1)   # a hair above a keyword: the label says what the business is
        phr[_norm(n["id"].replace("_", " "))] = 2.0
        for s in n["services"]:
            phr[_norm(s)] = max(phr.get(_norm(s), 0), 1.5)
        bag = {}
        for p, w in phr.items():
            for t in _tokens(p):
                bag[t] = max(bag.get(t, 0), 1.15 if w > 3 else (1.0 if w >= 3 else 0.45))
        for t in bag:
            df[t] = df.get(t, 0) + 1
        entries.append({"id": n["id"], "phrases": phr, "bag": bag})
    N = len(entries)
    idf = {t: math.log((N + 1) / (c + 0.5)) for t, c in df.items()}
    types = []
    for t in W.spec()["types"]:
        types.append({"theme": t["theme"], "text": _norm(t["type_text"])})
    return (entries, idf, types)


def _vocab():
    if "v" not in _cache:
        from . import typos
        words = typos._load()[0]
        niche_words = set()
        for e in _index()[0]:
            niche_words.update(e["bag"])
        _cache["v"] = (words, {w for w in niche_words if w.isascii() and len(w) >= 5})
    return _cache["v"]


def fix_typos(text):
    """"pest controll", "cockroch", "tatoo studio": a word nobody knows that is one slip away from a word of the niche vocabulary is read as that word."""
    from . import typos
    words, niche = _vocab()
    changes = []

    def one(m):
        w = m.group(0)
        if len(w) < 5 or w in words or w in niche or STEM.sub("", w) in niche or STEM.sub("", w) in words:
            return w
        best = None
        for c in niche:
            if abs(len(c) - len(w)) <= 1 and c[0] == w[0]:
                d = typos._dist(w, c)
                if d <= (1 if len(w) <= 8 else 2) and (best is None or d < best[0]):
                    best = (d, c)
        if best:
            changes.append((w, best[1]))
            return best[1]
        return w
    return re.sub(r"(?<![A-Za-z@./-])[a-z]{5,20}(?![A-Za-z@./-])", one, text), changes


def rebuild(drop=None):
    """Forget the index. (The hold-out test passes `drop` to understand() itself; nothing is kept between calls.)"""
    with _lock:
        _cache.pop("i", None)


def _score(text, entry, idf, drop):
    norm = " " + _norm(text) + " "
    toks = set(_tokens(text))
    s = 0.0
    for p, w in entry["phrases"].items():
        if not p or (drop and p in drop.get(entry["id"], ())):
            continue
        if " " + p + " " in norm:
            s += w * (1 + 0.6 * (len(p.split()) - 1))
    for t in toks:
        if t in entry["bag"]:
            s += entry["bag"][t] * idf.get(t, 1.0) * 0.8
    return s


def lang_of(req):
    return "hi" if any("\u0900" <= ch <= "\u097f" for ch in req) else "x"


def detect_lang(req):
    if any("ऀ" <= ch <= "ॿ" for ch in req):
        return "hi"
    return "hinglish" if HINGLISH.search(req) else "en"


def understand(req, drop=None):
    """-> dict(niche, type_theme, brand, city, lang, confidence, scores). niche is a niche id or None; when None, type_theme tells which general pack to use."""
    req = " ".join(str(req).split())[:600]
    entries, idf, types = _index()
    brand = None
    m = BRAND_RX.search(req)
    if m:
        brand = clean_name(m.group(1) or m.group(2))
    city = None
    for cm in CITY_RX.finditer(req):
        c = clean_name(cm.group(1) or cm.group(2) or "", "city")
        if c and c.lower() not in ("create", "make", "build", "a", "an", "the") and not (brand and c in brand):
            city = c
            break
    text = req
    if city:
        text = re.sub(r"\b(?:in|at|near|based in)\s+" + re.escape(city) + r"\b|\b" + re.escape(city) + r"\s+(?:mein|me)\b", " ", text)
    if brand:
        text = text.replace(brand, " ")
    typo_changes = []
    if lang_of(req) != "hi":
        text, typo_changes = fix_typos(text)
    low = " " + _norm(text) + " "
    for f in sorted(FLUFF, key=len, reverse=True):
        low = low.replace(" " + _norm(f) + " ", " ")
    core = low.strip()
    lang = detect_lang(req)
    # "Create a modern website for <type>": the request names one of the 20 business types, not a trade
    for t in types:
        if t["text"] and (" " + t["text"] + " ") in (" " + _norm(req) + " ") and len(t["text"].split()) >= 3:
            return {"niche": None, "type_theme": t["theme"], "brand": brand, "city": city, "lang": lang, "confidence": 1.0, "scores": [], "core": core}
    scored = sorted(((_score(core or req, e, idf, drop), e["id"]) for e in entries), reverse=True)
    best, second = scored[0], scored[1]
    conf = (best[0] - second[0]) / best[0] if best[0] > 0 else 0.0
    result = {"niche": None, "type_theme": None, "brand": brand, "city": city, "lang": lang, "confidence": round(conf, 3), "scores": [(round(a, 2), b) for a, b in scored[:3]], "core": core, "typos": typo_changes}
    if best[0] >= 2.0 or (best[0] >= 1.2 and conf >= 0.1):   # one weak word is enough only when it points to one niche clearly
        result["niche"] = best[1]
        return result
    # nothing specific: a type word ("travel website", "software") picks a general pack, a vague request gets the general local business pack
    theme = _type_of(core or _norm(req), types)
    result["type_theme"] = theme or "general_business"
    result["vague"] = theme is None
    return result


def _type_of(core, types):
    toks = set(_tokens(core))
    best, theme = 0, None
    for theme_id, spec in TYPES.items():
        words = {STEM.sub("", w) for k in spec[3] for w in _norm(k).split()} | {STEM.sub("", w) for w in _norm(spec[0]).split()}
        words -= STOP | {"and", "business"}
        hit = len(toks & words)
        if hit > best:
            best, theme = hit, theme_id
    return theme if best else None
