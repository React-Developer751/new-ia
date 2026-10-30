"""Write the packs the training spec asks for: batch-1.json ... (arrays of niche packs, 10 niches each) and type-packs.json (the 20 business types), then check them.
Run: python3 training/export_packs.py [out_dir]   (default output/niche_packs)"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from corecraft import pack_check, pack_writer as W   # noqa: E402
from corecraft.pack_niches import MENUS   # noqa: E402


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "output" / "niche_packs"
    out.mkdir(parents=True, exist_ok=True)
    packs = [W.build_pack(n) for n in W.spec()["niches"]]
    types = W.build_type_packs()
    foods = set(MENUS) | {"type_food_dining"}
    problems = pack_check.check_batch(packs + types, foods=foods)
    for i in range(0, len(packs), 10):
        (out / ("batch-%d.json" % (i // 10 + 1))).write_text(json.dumps(packs[i:i + 10], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "type-packs.json").write_text(json.dumps(types, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("niche packs: %d in %d files | business-type packs: %d | %d problems" % (len(packs), (len(packs) + 9) // 10, len(types), len(problems)))
    for p in problems[:20]:
        print("  ", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
