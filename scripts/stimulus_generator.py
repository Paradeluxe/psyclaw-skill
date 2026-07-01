#!/usr/bin/env python3
"""stimulus_generator.py — Generate stimulus asset files."""
import argparse, asyncio, json, math, struct, subprocess, sys, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def _color_to_rgb(color):
    if isinstance(color, str):
        names = {"white": (255,255,255),"black":(0,0,0),"red":(255,0,0),"green":(0,255,0),
                 "blue":(0,0,255),"yellow":(255,255,0),"cyan":(0,255,255),"magenta":(255,0,255),
                 "gray":(128,128,128),"grey":(128,128,128)}
        return names.get(color.lower(), (255,255,255))
    if isinstance(color, (list, tuple)) and len(color) == 3:
        if max(color) <= 1.0: return tuple(int(c * 255) for c in color)
        return tuple(int(c) for c in color)
    return (255,255,255)

def _resolve_size(size):
    if isinstance(size[0], float) and size[0] < 10:
        return [int(size[0] * 800), int(size[1] * 800)]
    return [int(size[0]), int(size[1])]

def _try_load_font(size_px, font_name="Arial"):
    candidates = [font_name, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for c in candidates:
        if not c: continue
        try: return ImageFont.truetype(c, int(size_px))
        except: pass
    return ImageFont.load_default()

def generate_image_text(spec, out_path):
    size = _resolve_size(spec.get("size", [200, 200]))
    bg = _color_to_rgb(spec.get("background", [0,0,0]))
    fg = _color_to_rgb(spec.get("foreground", [1,1,1]))
    text = spec.get("text", "+")
    font_name = spec.get("font", "Arial")
    fmt = spec.get("format", "png").lower()
    img = Image.new("RGB", tuple(size), bg)
    draw = ImageDraw.Draw(img)
    if text == "+":
        line_w = max(2, int(min(size) * 0.05)); length = int(min(size) * 0.6)
        cx, cy = size[0]//2, size[1]//2
        draw.rectangle([cx-length//2, cy-line_w//2, cx+length//2, cy+line_w//2], fill=fg)
        draw.rectangle([cx-line_w//2, cy-length//2, cx+line_w//2, cy+length//2], fill=fg)
    elif text == "-":
        line_w = max(2, int(min(size) * 0.05)); length = int(min(size) * 0.6)
        cy = size[1]//2
        draw.rectangle([(size[0]-length)//2, cy-line_w//2, (size[0]+length)//2, cy+line_w//2], fill=fg)
    else:
        font = _try_load_font(int(min(size) * 0.4), font_name)
        bbox = draw.textbbox((0,0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text(((size[0]-tw)//2-bbox[0], (size[1]-th)//2-bbox[1]), text, font=font, fill=fg)
    img.save(str(out_path), fmt.upper())
    return out_path

def generate_image_shape(spec, out_path):
    size = _resolve_size(spec.get("size", [200, 200]))
    bg = _color_to_rgb(spec.get("background", [0.5,0.5,0.5]))
    color = _color_to_rgb(spec.get("color", [1,1,1]))
    shape = spec.get("shape", "circle")
    radius = spec.get("radius", min(size)//3)
    img = Image.new("RGB", tuple(size), bg)
    draw = ImageDraw.Draw(img)
    cx, cy = size[0]//2, size[1]//2
    if shape == "circle":
        draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=color)
    elif shape == "rect":
        draw.rectangle([cx-radius, cy-radius, cx+radius, cy+radius], fill=color)
    elif shape == "polygon":
        points = []
        for i in range(6):
            a = math.radians(60*i-30)
            points.append((cx+radius*math.cos(a), cy+radius*math.sin(a)))
        draw.polygon(points, fill=color)
    img.save(str(out_path), "PNG")
    return out_path

def generate_audio_tone(spec, out_path):
    duration = spec.get("duration", 0.3); freq = spec.get("frequency", 880)
    sample_rate = 44100; n_samples = int(duration * sample_rate)
    out_path = Path(out_path).with_suffix(".wav")
    with wave.open(str(out_path), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            env = 1.0
            fade = int(0.01 * sample_rate)
            if i < fade: env = i / fade
            elif i > n_samples - fade: env = (n_samples - i) / fade
            val = int(env * 32767 * 0.5 * math.sin(2 * math.pi * freq * t))
            w.writeframes(struct.pack("<h", val))
    if spec.get("format", "wav").lower() == "mp3":
        mp3 = out_path.with_suffix(".mp3")
        subprocess.run(["ffmpeg","-y","-i",str(out_path),"-codec:a","libmp3lame","-qscale:a","2",str(mp3)], capture_output=True, check=True)
        out_path.unlink(); out_path = mp3
    return out_path

async def _tts_one(text, voice, out_path):
    import edge_tts
    await edge_tts.Communicate(text, voice).save(str(out_path))

def generate_audio_tts(spec, out_path):
    text = spec.get("text", ""); voice = spec.get("voice", "en-US-AriaNeural")
    out_path = Path(out_path).with_suffix(".wav")
    tmp = out_path.with_suffix(".mp3")
    asyncio.run(_tts_one(text, voice, tmp))
    subprocess.run(["ffmpeg","-y","-i",str(tmp),str(out_path)], capture_output=True, check=True)
    tmp.unlink()
    return out_path

def generate_video_animated_shape(spec, out_path):
    size = _resolve_size(spec.get("size", [400,400]))
    duration = spec.get("duration", 2.0); fps = spec.get("fps", 30)
    n_frames = max(2, int(duration * fps))
    bg = _color_to_rgb(spec.get("background", [0,0,0]))
    color = _color_to_rgb(spec.get("color", [1,0,0]))
    shape = spec.get("shape", "circle")
    r_start = spec.get("start_radius", 10); r_end = spec.get("end_radius", 100)
    out_path = Path(out_path).with_suffix(".mp4")
    frame_dir = out_path.parent / f"_frames_{out_path.stem}"
    frame_dir.mkdir(exist_ok=True)
    for i in range(n_frames):
        t = i / (n_frames - 1); r = int(r_start + (r_end-r_start)*t)
        img = Image.new("RGB", tuple(size), bg)
        draw = ImageDraw.Draw(img)
        cx, cy = size[0]//2, size[1]//2
        if shape == "circle": draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=color)
        elif shape == "rect": draw.rectangle([cx-r,cy-r,cx+r,cy+r], fill=color)
        img.save(frame_dir / f"frame_{i:05d}.png")
    subprocess.run(["ffmpeg","-y","-framerate",str(fps),"-i",str(frame_dir/"frame_%05d.png"),
                    "-c:v","libx264","-pix_fmt","yuv420p",
                    "-vf","scale=trunc(iw/2)*2:trunc(ih/2)*2",str(out_path)],
                   capture_output=True, check=True)
    for f in frame_dir.glob("*.png"): f.unlink()
    frame_dir.rmdir()
    return out_path

def generate_stimulus(stim, out_dir, verbose=False):
    sid = stim.get("id")
    if not sid: return None
    if "external" in stim:
        path = Path(stim["external"]); return path if path.exists() else None
    out_path = out_dir / (sid + "." + stim.get("format", "png"))
    kind = stim.get("kind"); generator = stim.get("generator", "")
    if kind == "text": return None
    elif kind == "image":
        if generator == "text": generate_image_text(stim, out_path)
        else: generate_image_shape(stim, out_path)
    elif kind == "audio":
        if generator == "tts": generate_audio_tts(stim, out_path)
        else: generate_audio_tone(stim, out_path)
    elif kind == "video":
        generate_video_animated_shape(stim, out_path)
    else: return None
    if verbose and out_path.exists():
        print(f"  [stim] {sid}: {out_path} ({out_path.stat().st_size} bytes)")
    return out_path

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec"); ap.add_argument("--stim")
    ap.add_argument("--out-dir", default="assets")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    if not args.spec and not args.stim:
        print("[FATAL] provide --spec or --stim", file=sys.stderr); return 1
    if args.spec:
        import yaml
        with open(args.spec) as f: spec = yaml.safe_load(f)
        stimuli = spec.get("stimuli", [])
    else:
        with open(args.stim) as f: stimuli = json.load(f)
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for stim in stimuli:
        if generate_stimulus(stim, out_dir, verbose=args.verbose): n += 1
    print(f"[stimgen] generated {n}/{len(stimuli)} stimuli in {out_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
