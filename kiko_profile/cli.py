"""
Command line interface for kiko-profile.
"""

import argparse
import os
import sys
from typing import Optional

from kiko_profile.activity import fetch_github_activity
from kiko_profile.evolution import determine_evolution
from kiko_profile.generator import save_kiko_outputs


def main(args: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kiko-profile",
        description="Draw an animated pixel-art snapping turtle walking across your GitHub profile README.",
    )
    parser.add_argument("username", help="GitHub username whose activity to draw")
    parser.add_argument(
        "--output-dir",
        default="kiko",
        help="Directory to save kiko.gif, kiko.png, and preview.html (default: 'kiko')",
    )
    parser.add_argument(
        "--stage",
        choices=["auto", "baby", "juvenile", "titan"],
        default="auto",
        help="Evolution stage (default: auto, determined from contribution volume)",
    )
    parser.add_argument(
        "--background",
        "--theme",
        dest="background",
        default="transparent",
        help="Background style: 'transparent', 'dark' (#0d1117), or custom hex (default: 'transparent')",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=840,
        help="Canvas banner width in pixels (default: 840)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=80,
        help="Canvas banner height in pixels (default: 80)",
    )
    parser.add_argument(
        "--token",
        help="GitHub token for authenticated GraphQL API (or set GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch stats and validate pipeline without writing files to disk",
    )

    parsed = parser.parse_args(args)
    token = parsed.token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    print(f"[kiko-profile] Fetching activity for @{parsed.username}...")
    try:
        activity = fetch_github_activity(parsed.username, token=token)
        print(f"[kiko-profile] Total contributions: {activity.total_contributions:,} | Current streak: {activity.current_streak} days")
    except Exception as e:
        print(f"[kiko-profile] Warning: Could not fetch live stats ({e}). Using fallback activity profile.", file=sys.stderr)
        from kiko_profile.activity import AccountActivity
        activity = AccountActivity(
            username=parsed.username,
            total_contributions=350,
            current_streak=5,
            longest_streak=12,
            contributions_today=1,
            top_languages=["Python", "Swift"],
            language_colors={"Python": "#3572A5", "Swift": "#F05138"},
        )

    forced = None if parsed.stage == "auto" else parsed.stage
    evolution = determine_evolution(activity, forced_stage=forced)
    print(f"[kiko-profile] Form: {evolution.stage_title} | Pace: {evolution.pace_description} ({evolution.frame_duration_ms}ms)")

    if parsed.dry_run:
        print("[kiko-profile] Dry run complete.")
        return 0

    print(f"[kiko-profile] Rendering walking animation across {parsed.width}x{parsed.height}px banner ({parsed.background})...")
    outputs = save_kiko_outputs(
        activity=activity,
        evolution=evolution,
        output_dir=parsed.output_dir,
        canvas_width=parsed.width,
        canvas_height=parsed.height,
        background=parsed.background,
    )

    print(f"[kiko-profile] [SUCCESS] Wrote animation to: {outputs['gif']}")
    print(f"[kiko-profile] [SUCCESS] Wrote preview to:   {outputs['preview']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
