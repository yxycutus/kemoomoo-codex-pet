from PIL import Image, ImageDraw
from pathlib import Path
p=Path(__file__).resolve().parent.parent
(p/'qa').mkdir(exist_ok=True)
a=Image.open(p/'final/spritesheet.png').convert('RGBA')
seq=[('idle5',0,5)]+[('jump'+str(i),4,i) for i in range(5)]+[('idle0',0,0)]
out=Image.new('RGBA',(192*7,232),'#dddddd')
d=ImageDraw.Draw(out)
for i,(name,y,x) in enumerate(seq):
    cell=a.crop((x*192,y*208,(x+1)*192,(y+1)*208))
    out.alpha_composite(cell,(i*192,24))
    d.text((i*192+6,4),name,fill='black')
    print(name,cell.getbbox())
out.save(p/'qa/jump-transition-review.png')
for f in (p/'qa').rglob('*.gif'):
    if f.parent.name=='\u9884\u89c8\u521d\u7248':
        im=Image.open(f)
        print(f.name,im.n_frames,im.info.get('duration'))
