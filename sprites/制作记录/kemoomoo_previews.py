"""Render existing atlas pixels only; no character drawing or animation synthesis."""
import sys
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent  # 科哞哞桌宠目录
SKILL = Path('~/.codex/plugins/cache/openai-curated-remote/work-pets/0.1.6/skills/create-pet/scripts').expanduser()
sys.path.insert(0, str(SKILL))
from render_animation_previews import ROW_DURATIONS, save_preview
atlas_path = Path(sys.argv[1])
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
atlas = Image.open(atlas_path).convert('RGBA')
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
names = ['待机', '向右奔跑', '向左奔跑', '挥手', '跳跃', '出错大哭', '等待回应', '工作思考', '检查成果']
cell = lambda r,c: atlas.crop((c*192,r*208,(c+1)*192,(r+1)*208))
all_frames, all_times = [], []
frames_root = out / 'encoded-frames'
for row,(state,durations) in enumerate(ROW_DURATIONS.items()):
    state_dir = frames_root / state
    state_dir.mkdir(parents=True, exist_ok=True)
    for index,duration in enumerate(durations):
        sprite = cell(row,index)
        sprite.save(state_dir / f'{index:02d}.png')
        panel = Image.new('RGBA',(320,280),(244,247,250,255))
        panel.alpha_composite(sprite,(64,28))
        ImageDraw.Draw(panel).text((16,250),f'{names[row]} · {index+1}/{len(durations)}',font=font,fill=(37,54,77,255))
        all_frames.append(panel)
        all_times.append(duration)
save_preview(all_frames,all_times,out/'全部动作.gif')
transition = [cell(0,0),cell(0,4),*[cell(4,c) for c in range(5)],cell(0,5),cell(0,0)]
save_preview(transition,[500,250,140,140,140,140,280,250,500],out/'待机到跳跃.gif')
if atlas.height == 2288:
    directions = [cell(9+i//8,i%8) for i in range(16)]
    save_preview(directions,[180]*16,out/'视线跟随.gif')
stills = Image.new('RGBA',(768,248),(244,247,250,255))
for k,(r,c) in enumerate([(1,0),(1,3),(5,2),(4,2)]):
    stills.alpha_composite(cell(r,c),(k*192,16))
    ImageDraw.Draw(stills).text((k*192+8,226),f'{names[r]} · 帧{c+1}',font=font,fill=(37,54,77,255))
stills.save(out/'动作关键帧.png')
subprocess.run([sys.executable,str(SKILL/'render_animation_previews.py'),'--frames-root',str(frames_root),'--output-dir',str(out/'单项动作')],check=True,capture_output=True)
try:
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    ffmpeg = 'ffmpeg'
subprocess.run([str(ffmpeg),'-y','-loglevel','error','-i',str(out/'全部动作.gif'),'-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'全部动作.mp4')],check=True)
(out/'preview-source.json').write_text(json.dumps({'atlas':str(atlas_path),'bytes':atlas_path.stat().st_size,'rendered_from_encoded_atlas':True},indent=2),encoding='utf-8')
print('Rendered previews from '+str(atlas_path))
