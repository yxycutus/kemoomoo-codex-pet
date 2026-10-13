"""Read-only release checks. Run with Python 3.10+ and Pillow."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
files = subprocess.check_output(
    ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT
).decode('utf-8').split('\0')
files = sorted({f for f in files if f})
errors = []
counts = {'files': len(files), 'images': 0, 'json': 0, 'local_links': 0}

def check(condition, message):
    if not condition:
        errors.append(message)

def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))

for name in files:
    path = ROOT / name
    check(path.is_file(), f'Missing file: {name}')
    if not path.is_file():
        continue
    check(path.stat().st_size < 100 * 1024 * 1024, f'GitHub file size limit: {name}')
    if path.suffix.lower() in {'.png', '.webp', '.gif', '.apng', '.jpg', '.jpeg'}:
        try:
            with Image.open(path) as im:
                for frame in range(getattr(im, 'n_frames', 1)):
                    im.seek(frame)
                    im.load()
            counts['images'] += 1
        except Exception as error:
            errors.append(f'Image decode failed: {name}: {error}')
    if path.suffix == '.json':
        try:
            load(name)
            counts['json'] += 1
        except Exception as error:
            errors.append(f'JSON invalid: {name}: {error}')
    if path.suffix in {'.md', '.json', '.py', '.js', '.cjs', '.txt', '.html', '.css'}:
        text = path.read_text(encoding='utf-8-sig')
        # Match actual user-specific paths, never print matched contents.
        check(not re.search(r'[A-Za-z]:[\\/]+Users[\\/]+\w|/(?:Users|home)/[\w.-]+/', text),
              f'User-specific absolute path: {name}')
        check(not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)', text),
              f'Potential credential: {name}')
    if path.suffix == '.md':
        text = path.read_text(encoding='utf-8-sig')
        check(not re.search(r'^\s*`(?:html|javascript|bash)?\s*$', text, re.M), f'Broken code fence: {name}')
        for link in re.findall(r'\]\(([^)]+)\)', text):
            link = unquote(link.split('#')[0].split(' "')[0].strip('<>'))
            if not link or re.match(r'\w+:', link):
                continue
            counts['local_links'] += 1
            check((path.parent / link).exists(), f'Broken local link in {name}: {link}')

frames = [6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8]
for name, rows in [('sprites/final/spritesheet-extended.png', 11),
                   ('web/pet/spritesheet.webp', 11), ('web/pet/spritesheet.png', 11),
                   ('codex/kemoomoo/spritesheet.png', 9)]:
    with Image.open(ROOT / name) as im:
        check(im.mode == 'RGBA', f'RGBA required: {name}')
        check(im.size == (1536, rows * 208), f'Atlas size: {name}')
        for row in range(rows):
            for col in range(8):
                alpha = im.crop((col*192, row*208, (col+1)*192, (row+1)*208)).getchannel('A')
                check(bool(alpha.getbbox()) == (col < frames[row]), f'Cell occupancy {name} row={row} col={col}')
        check(im.getchannel('A').getextrema() == (0,255), f'Transparency: {name}')

atlas = (ROOT/'sprites/final/spritesheet-extended.png').read_bytes()
check(atlas == (ROOT/'web/pet/spritesheet.png').read_bytes(), 'PNG fallback differs from final atlas')
check((ROOT/'codex/kemoomoo/spritesheet.png').read_bytes() == (ROOT/'sprites/final/spritesheet.png').read_bytes(), 'Desktop package differs from nine-row source')
for name in ['sprites/final/validation-extended.json', 'sprites/qa/pet-quality.json']:
    check(load(name)['sha256'] == hashlib.sha256(atlas).hexdigest(), f'Outdated QA hash: {name}')
pet = load('codex/kemoomoo/pet.json')
check(pet['id'] == 'kemoomoo' and bool(pet['displayName']), 'Desktop pet identity')
check((ROOT/'codex/kemoomoo'/pet['spritesheetPath']).is_file(), 'Desktop manifest image path')
request = load('sprites/pet_request.json')
check([row['frames'] for row in request['rows']] == frames, 'Frame configuration mismatch')
for guide in request['layout_guides']:
    check((ROOT/'sprites'/guide['path'].replace('\\','/')).is_file(), f'Missing layout guide: {guide["state"]}')
for item in load('web/pet/scenes.json')['scenes']:
    check((ROOT/'web/pet'/item['file']).is_file(), f'Missing scene {item["id"]}')
    with Image.open(ROOT/'web/pet/cutouts'/f'{item["id"]}.webp') as im:
        check(im.size == (512,512) and im.mode == 'RGBA', f'Invalid cutout: {item["id"]}')
        check(im.getchannel('A').getextrema() == (0,255), f'Cutout transparency: {item["id"]}')
for path in ROOT.rglob('*.py'):
    if '.git' not in path.parts and 'node_modules' not in path.parts:
        compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec')
print(json.dumps({'ok': not errors, 'counts': counts, 'errors': errors}, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
