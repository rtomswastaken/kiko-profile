"""
Evolution & behavioral rules for Kiko the Snapping Turtle.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from kiko_profile.activity import AccountActivity


@dataclass
class TurtleEvolution:
    stage_name: str         # "baby", "juvenile", "titan"
    stage_title: str        # e.g., "Apex Titan Snapper"
    frame_duration_ms: int  # Speed of the walk animation (lower is faster)
    pace_description: str   # "energetic stride", "steady crawl", "leisurely amble"
    scale_height: int       # Rendered pixel height of the turtle
    accent_color: Optional[str] = None  # Primary language accent color (hex)


def determine_evolution(activity: AccountActivity, forced_stage: Optional[str] = None) -> TurtleEvolution:
    """
    Determine the stage, walk cadence, and visual properties based on GitHub stats.
    """
    total = activity.total_contributions
    
    if forced_stage and forced_stage.lower() in ("baby", "juvenile", "titan"):
        stage = forced_stage.lower()
    else:
        if total < 150:
            stage = "baby"
        elif total < 500:
            stage = "juvenile"
        else:
            stage = "titan"

    if stage == "baby":
        title = "Baby Hatchling Kiko"
        base_height = 54
    elif stage == "titan":
        title = "Apex Titan Snapper"
        base_height = 70
    else:
        title = "Juvenile Snapping Turtle"
        base_height = 62

    # Gait & pacing based on streaks and today's activity
    if activity.contributions_today > 0 or activity.current_streak >= 5:
        duration = 55
        pace = "energetic stride"
    elif activity.current_streak >= 2:
        duration = 65
        pace = "steady crawl"
    else:
        duration = 80
        pace = "leisurely amble"

    # Primary language color
    accent = None
    if activity.top_languages:
        primary = activity.top_languages[0]
        accent = activity.language_colors.get(primary)

    return TurtleEvolution(
        stage_name=stage,
        stage_title=title,
        frame_duration_ms=duration,
        pace_description=pace,
        scale_height=base_height,
        accent_color=accent,
    )
