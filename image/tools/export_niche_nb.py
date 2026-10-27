#!/usr/bin/env python3
"""Copy the trained niche classifier out of a model file into the package, so the studio understands prompts without any model file.

    python3 train.py studio_data/train --model studio_model.json
    python3 tools/export_niche_nb.py studio_model.json
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pixelmath.learn import LearnedModel  # noqa: E402


def main(argv):
    if not argv:
        sys.exit(__doc__)
    nb = LearnedModel.load(argv[0]).extras.get("niche_nb")
    if not nb:
        sys.exit("this model has no niche classifier (train on a manifest with niche labels first)")
    out = os.path.join(ROOT, "pixelmath", "studio", "niche_nb.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(nb, fh, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    print("wrote %s (%d classes, %d words, %d bytes)" % (out, len(nb["classes"]), nb["vocab"], os.path.getsize(out)))


if __name__ == "__main__":
    main(sys.argv[1:])
