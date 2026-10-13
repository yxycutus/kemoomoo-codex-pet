"""Run the actual bundled pet gates on the completed artwork."""
from pathlib import Path
import subprocess
import sys
from PIL import Image

root = Path(r'C:\Users\jojo\Documents\Codex\2026-10-12\new-chat\outputs\科哞哞桌宠')
skill = Path(r'C:\Users\jojo\.codex\plugins\cache\openai-curated-remote\work-pets\0.1.6\skills\create-pet\scripts')
final = root/'final'/'spritesheet-extended.png'
qa = root/'qa'

def run(script,*args):
    p = subprocess.run([sys.executable,str(skill/script),*map(str,args)],capture_output=True,text=True)
    (qa/(script.removesuffix('.py')+'-execution.txt')).write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
    if p.returncode:
        print(p.stdout,p.stderr)
        raise SystemExit(p.returncode)
    print(script+': completed')

run('despill_chroma_edges.py',root/'final'/'spritesheet-extended-raw.png','--output',final,'--json-out',qa/'chroma-despill-extended.json','--chroma-key','#00FF00')
run('validate_atlas.py',final,'--require-v2','--chroma-key','#00FF00','--json-out',root/'final'/'validation-extended.json')
run('make_contact_sheet.py',final,'--output',qa/'contact-sheet-final.png','--scale','1')
run('make_direction_qa_sheet.py',final,'--output',qa/'direction-qa.png')
run('measure_direction_continuity.py',final,'--json-out',qa/'look-continuity.json')
run('make_direction_blind_qa_sheet.py',final,'--output',qa/'blind-directions.png','--answer-key',qa/'blind-answer-key.json')
with Image.open(qa/'blind-directions.png') as im:
    im.crop((0,0,im.width,7*236)).save(qa/'blind-horizontal.png')
    im.crop((0,7*236,im.width,im.height)).save(qa/'blind-vertical.png')
subprocess.run([sys.executable,str(Path(__file__).with_name('kemoomoo_previews.py')),str(final),str(root/'动画预览')],check=True)
