"""
Sprite loading, background extraction, and palette tinting for Kiko the Snapping Turtle.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image

ASSETS_DIR = Path(__file__).parent / "assets"
DEFAULT_SHEET_PATH = ASSETS_DIR / "kiko_spritesheet.png"


def load_master_sheet(sheet_path: Optional[Path] = None) -> Image.Image:
    path = sheet_path or DEFAULT_SHEET_PATH
    if not path.exists():
        raise FileNotFoundError(f"Master spritesheet not found at: {path}")
    return Image.open(path).convert("RGBA")


def extract_masked_sprite(
    sheet: Image.Image,
    box: Tuple[int, int, int, int],
    bg_color: Tuple[int, int, int] = (14, 18, 27),
) -> Image.Image:
    """
    Crops a region from the spritesheet and applies soft alpha masking to remove the background,
    returning a clean RGBA transparent sprite tightly bounded to the sprite pixels.
    """
    crop = sheet.crop(box)
    arr = np.array(crop).astype(float)
    
    # Calculate Euclidean distance in RGB from the background color
    dist = np.sqrt(np.sum((arr[:, :, :3] - np.array(bg_color, dtype=float)) ** 2, axis=-1))
    
    # Smooth alpha transition around the boundary
    alpha = np.clip((dist - 14) / 12.0 * 255.0, 0, 255).astype(np.uint8)
    
    out_arr = arr.astype(np.uint8)
    out_arr[:, :, 3] = alpha
    
    # Find bounding box of opaque pixels
    y_idx, x_idx = np.where(alpha > 45)
    if len(y_idx) == 0:
        return crop
    ymin, ymax = y_idx.min(), y_idx.max()
    xmin, xmax = x_idx.min(), x_idx.max()
    
    return Image.fromarray(out_arr[ymin:ymax + 1, xmin:xmax + 1], mode="RGBA")


def get_stage_sprites(stage: str, target_height: int = 62) -> List[Image.Image]:
    """
    Returns a 4-frame walk cycle for the requested stage:
    'baby', 'juvenile', or 'titan'.
    """
    sheet = load_master_sheet()

    if stage == "baby":
        base_baby = extract_masked_sprite(sheet, (80, 520, 360, 715))
        # Build 4 walk frames by subtle alternating foot & shell shifts
        frames = []
        w_target = int(base_baby.width * (target_height / base_baby.height))
        resized = base_baby.resize((w_target, target_height), Image.Resampling.LANCZOS)
        
        # Frame 1: Base
        frames.append(resized)
        # Frame 2: Step forward right (1px drop)
        f2 = Image.new("RGBA", resized.size, (0, 0, 0, 0))
        f2.paste(resized, (0, 1), resized)
        frames.append(f2)
        # Frame 3: Base
        frames.append(resized)
        # Frame 4: Step forward left (1px lift)
        f4 = Image.new("RGBA", resized.size, (0, 0, 0, 0))
        f4.paste(resized, (0, 0), resized)
        frames.append(f4)
        return frames

    elif stage == "titan":
        base_titan = extract_masked_sprite(sheet, (800, 440, 1340, 715))
        w_target = int(base_titan.width * (target_height / base_titan.height))
        resized = base_titan.resize((w_target, target_height), Image.Resampling.LANCZOS)
        
        # Titan heavy crawl frames
        frames = []
        frames.append(resized)
        
        f2 = Image.new("RGBA", resized.size, (0, 0, 0, 0))
        f2.paste(resized, (0, 1), resized)
        frames.append(f2)
        
        frames.append(resized)
        
        f4 = Image.new("RGBA", resized.size, (0, 0, 0, 0))
        f4.paste(resized, (0, 0), resized)
        frames.append(f4)
        return frames

    else:
        # Juvenile 4-frame drawn walk cycle
        walk_crops = [
            (670, 95, 985, 235),
            (995, 95, 1315, 235),
            (670, 245, 985, 385),
            (995, 245, 1315, 385),
        ]
        raw_frames = [extract_masked_sprite(sheet, box) for box in walk_crops]
        resized_frames = []
        for f in raw_frames:
            w_target = int(f.width * (target_height / f.height))
            resized_frames.append(f.resize((w_target, target_height), Image.Resampling.LANCZOS))
        return resized_frames
