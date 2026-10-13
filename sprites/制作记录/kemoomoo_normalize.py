"""Uniform row registration after the bundled component extractor.

No pet artwork is drawn. Every row receives one shared transform; the jumping
row preserves its generated airborne positions and uses its landing pose as
the standing-height reference.
"""
from pathlib import Path
import json
import statistics
from PIL import Image

ROOT = Path(r'C:\Users\jojo\Documents\Codex\2026-10-12\new-chat\outputs\科哞哞桌宠')
FRAMES = ROOT / 'frames'
TARGET_HEIGHT = 152
TARGET_BASELINE = 200
STATES = ['idle', 'running-right', 'running-left', 'waving', 'jumping', 'failed', 'waiting', 'running', 'review']
report = []
for state in STATES:
    paths = sorted((FRAMES / state).glob('*.png'))
    originals = [Image.open(p).convert('RGBA') for p in paths]
    boxes = [im.getchannel('A').point(lambda a: 255 if a > 16 else 0).getbbox() for im in originals]
    if state == 'jumping':
        reference_height = boxes[-1][3] - boxes[-1][1]
        baseline = boxes[-1][3]
    else:
        reference_height = statistics.median(b[3] - b[1] for b in boxes)
        baseline = statistics.median(b[3] for b in boxes)
    scale = TARGET_HEIGHT / reference_height
    size = (round(192 * scale), round(208 * scale))
    offset = (round(96 - 96 * scale), round(TARGET_BASELINE - baseline * scale))
    for path, im in zip(paths, originals):
        resized = im.resize(size, Image.Resampling.LANCZOS)
        out = Image.new('RGBA', (192, 208))
        out.alpha_composite(resized, offset)
        out.save(path)
    report.append({'state': state, 'shared_scale': scale, 'shared_offset': offset,
                   'reference_height': reference_height, 'source_baseline': baseline,
                   'target_baseline': TARGET_BASELINE, 'target_standing_height': TARGET_HEIGHT})
(ROOT / 'qa' / 'row-registration.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
