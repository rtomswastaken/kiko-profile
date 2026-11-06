"""
Animation generator for kiko-profile.
Compiles smooth walking GIF banners and still previews.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image

from kiko_profile.activity import AccountActivity
from kiko_profile.evolution import TurtleEvolution, determine_evolution
from kiko_profile.sprites import get_stage_sprites

GITHUB_DARK_HEX = "#0d1117"
GITHUB_DARK_RGB = (13, 17, 23)


def parse_color(color_spec: str) -> Optional[Tuple[int, int, int]]:
    """Parse color string into RGB tuple, or None for transparent."""
    clean = color_spec.strip().lower()
    if clean in ("transparent", "none", "alpha", ""):
        return None
    if clean in ("dark", "github-dark", "default-dark"):
        return GITHUB_DARK_RGB
    if clean in ("light", "white"):
        return (255, 255, 255)
    if clean.startswith("#"):
        hex_str = clean[1:]
        if len(hex_str) == 6:
            return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))
        elif len(hex_str) == 3:
            return (int(hex_str[0] * 2, 16), int(hex_str[1] * 2, 16), int(hex_str[2] * 2, 16))
    return GITHUB_DARK_RGB


def generate_walking_animation(
    evolution: TurtleEvolution,
    canvas_width: int = 840,
    canvas_height: int = 80,
    background: str = "transparent",
    steps_per_direction: int = 36,
) -> Tuple[List[Image.Image], Image.Image]:
    """
    Generates all frames for a full round-trip walk across the canvas width:
    Left -> Right, turn around, Right -> Left.
    Returns (animated_frames, hero_still_image).
    """
    sprites = get_stage_sprites(evolution.stage_name, target_height=evolution.scale_height)
    hero_sprite = sprites[0]
    
    bg_rgb = parse_color(background)
    is_transparent = bg_rgb is None
    
    spr_w, spr_h = hero_sprite.size
    y_pos = max(canvas_height - spr_h - 4, 2)
    
    x_min = 8
    x_max = max(canvas_width - spr_w - 8, x_min + 1)
    
    # Calculate smooth position arrays
    x_positions_right = np.linspace(x_min, x_max, steps_per_direction, dtype=int)
    x_positions_left = np.linspace(x_max, x_min, steps_per_direction, dtype=int)
    
    frames_right = sprites
    frames_left = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in sprites]
    
    composite_frames: List[Image.Image] = []
    
    # 1. Walk Right
    for i, x in enumerate(x_positions_right):
        frame = Image.new("RGBA", (canvas_width, canvas_height), (bg_rgb[0], bg_rgb[1], bg_rgb[2], 255) if not is_transparent else (0, 0, 0, 0))
        spr = frames_right[i % len(frames_right)]
        frame.paste(spr, (int(x), y_pos), spr)
        composite_frames.append(frame)
        
    # 2. Brief turning pause at right boundary
    turn_pause_right = Image.new("RGBA", (canvas_width, canvas_height), (bg_rgb[0], bg_rgb[1], bg_rgb[2], 255) if not is_transparent else (0, 0, 0, 0))
    turn_pause_right.paste(frames_right[0], (int(x_max), y_pos), frames_right[0])
    composite_frames.append(turn_pause_right)
    
    # 3. Walk Left
    for i, x in enumerate(x_positions_left):
        frame = Image.new("RGBA", (canvas_width, canvas_height), (bg_rgb[0], bg_rgb[1], bg_rgb[2], 255) if not is_transparent else (0, 0, 0, 0))
        spr = frames_left[i % len(frames_left)]
        frame.paste(spr, (int(x), y_pos), spr)
        composite_frames.append(frame)
        
    # 4. Brief pause at left boundary before loop
    turn_pause_left = Image.new("RGBA", (canvas_width, canvas_height), (bg_rgb[0], bg_rgb[1], bg_rgb[2], 255) if not is_transparent else (0, 0, 0, 0))
    turn_pause_left.paste(frames_left[0], (int(x_min), y_pos), frames_left[0])
    composite_frames.append(turn_pause_left)
    
    # Convert RGBA frames to quantized palette with transparency if requested
    quantized_frames: List[Image.Image] = []
    
    if is_transparent:
        # Create a crystal-clean palette with reserved transparency index 127
        for f in composite_frames:
            arr = np.array(f)
            mask_trans = arr[:, :, 3] <= 60
            
            # Extract RGB and quantize to 127 colors
            rgb_img = Image.fromarray(arr[:, :, :3], mode="RGB")
            p_img = rgb_img.quantize(colors=127, method=Image.Resampling.LANCZOS)
            
            p_arr = np.array(p_img)
            p_arr[mask_trans] = 127
            
            out_p = Image.fromarray(p_arr, mode="P")
            palette = list(p_img.getpalette())
            # Ensure index 127 has neutral dark background color
            palette[127 * 3 : 127 * 3 + 3] = [13, 17, 23]
            out_p.putpalette(palette)
            out_p.info["transparency"] = 127
            quantized_frames.append(out_p)
    else:
        for f in composite_frames:
            p_img = f.convert("RGB").quantize(colors=128, method=Image.Resampling.LANCZOS)
            quantized_frames.append(p_img)
            
    return quantized_frames, hero_sprite


def save_kiko_outputs(
    activity: AccountActivity,
    evolution: TurtleEvolution,
    output_dir: Union[Path, str],
    canvas_width: int = 840,
    canvas_height: int = 80,
    background: str = "transparent",
) -> Dict[str, Path]:
    """
    Generates and saves:
    - kiko.gif (walking animation)
    - kiko.png (still preview)
    - preview.html (visual inspection page)
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    frames, hero = generate_walking_animation(
        evolution=evolution,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        background=background,
    )
    
    gif_path = out_path / "kiko.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=evolution.frame_duration_ms,
        loop=0,
        disposal=2 if background.lower() in ("transparent", "none", "alpha", "") else 0,
        optimize=True,
    )
    
    png_path = out_path / "kiko.png"
    hero.save(png_path)
    
    # Generate HTML preview
    preview_path = out_path / "preview.html"
    html_content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>kiko-profile preview — @{activity.username}</title>
<style>
  body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; background: #010409; color: #e6edf3; padding: 24px; }}
  h1 {{ font-size: 20px; font-weight: 600; margin-bottom: 8px; }}
  .badge {{ display: inline-block; background: #21262d; padding: 4px 10px; border-radius: 12px; font-size: 13px; color: #58a6ff; margin-bottom: 20px; }}
  .box {{ border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 24px; overflow-x: auto; }}
  .box.dark {{ background: #0d1117; }}
  .box.light {{ background: #ffffff; color: #24292f; border-color: #d0d7de; }}
  .label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; margin-bottom: 12px; font-weight: 600; }}
  img {{ display: block; max-width: 100%; height: auto; image-rendering: pixelated; }}
  .stats {{ font-size: 14px; line-height: 1.8; color: #8b949e; }}
  .stats b {{ color: #e6edf3; }}
</style>
</head>
<body>
<h1>Kiko the Snapping Turtle — @{activity.username}</h1>
<div class="badge">{evolution.stage_title} • {evolution.pace_description} ({evolution.frame_duration_ms}ms)</div>

<div class="stats">
  <b>Total Contributions:</b> {activity.total_contributions:,} &nbsp;|&nbsp;
  <b>Current Streak:</b> {activity.current_streak} days &nbsp;|&nbsp;
  <b>Top Language:</b> {activity.top_languages[0] if activity.top_languages else "None"}
</div>

<br/>

<div class="box dark">
  <div class="label">GitHub Dark Theme Preview</div>
  <img src="kiko.gif" width="{canvas_width}" alt="Kiko Walking (Dark)">
</div>

<div class="box light">
  <div class="label" style="color: #57606a;">GitHub Light Theme Preview</div>
  <img src="kiko.gif" width="{canvas_width}" alt="Kiko Walking (Light)">
</div>

<div class="box dark">
  <div class="label">Still Avatar (kiko.png)</div>
  <img src="kiko.png" width="120" alt="Kiko Avatar">
</div>

</body>
</html>
"""
    preview_path.write_text(html_content, encoding="utf-8")
    
    return {
        "gif": gif_path,
        "png": png_path,
        "preview": preview_path,
    }
