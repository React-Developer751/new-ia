"""Pipeline: Content AI -> Image/Asset AI -> Design AI."""
import json
import re
from pathlib import Path

from . import asset_engine, content_engine, design_engine, photo_engine


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "site"


def run(prompt, out_root="output", seed=None, facts=None, lang=None, photos=True, photo_count=6):
    if not prompt or not prompt.strip():
        raise ValueError("prompt is empty")
    content = content_engine.generate_content(prompt, seed, facts=facts, lang=lang)
    assets = asset_engine.generate_assets(content, seed)
    asset_engine.validate_assets(assets)
    out_dir = Path(out_root) / slugify(content["brand"])
    pics = photo_engine.generate_photos(content, assets, out_dir, seed, photo_count) if photos else None
    if pics is not None and pics["fallback"]:
        content["needs_review"] = list(content.get("needs_review", [])) + [
            "No picture style fits this kind of business (%s): the pictures are a neutral abstract in the brand colour, not a wrong scene." % pics["reason"]]
    result = design_engine.generate_site(content, assets, out_dir, seed, pics)
    asset_engine.write_assets(assets, out_dir)
    pal = {k: v for k, v in assets["palette"].items() if k != "rgb"}
    (out_dir / "content.json").write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "palette.json").write_text(json.dumps(pal, indent=2), encoding="utf-8")
    result.update({"photos": None if pics is None else {k: pics[k] for k in ("niche", "fallback", "reason", "mood", "report")},
                   "brand": content["brand"], "niche": content["niche"], "business_type": content["business_type"], "needs_review": content["needs_review"], "missing": content.get("missing", []), "palette": pal})
    return result
