import os
import tempfile
import unittest
from PIL import Image

from kiko_profile.activity import AccountActivity
from kiko_profile.evolution import determine_evolution
from kiko_profile.generator import generate_walking_animation, save_kiko_outputs, parse_color
from kiko_profile.sprites import get_stage_sprites


class TestGenerator(unittest.TestCase):
    def test_parse_color(self):
        self.assertIsNone(parse_color("transparent"))
        self.assertIsNone(parse_color(""))
        self.assertEqual(parse_color("dark"), (13, 17, 23))
        self.assertEqual(parse_color("#ff0000"), (255, 0, 0))

    def test_get_stage_sprites(self):
        for stage in ("baby", "juvenile", "titan"):
            sprites = get_stage_sprites(stage, target_height=60)
            self.assertEqual(len(sprites), 4)
            for s in sprites:
                self.assertEqual(s.mode, "RGBA")
                self.assertGreater(s.width, 10)
                self.assertGreater(s.height, 10)

    def test_generate_walking_animation_transparent(self):
        act = AccountActivity(
            username="testuser",
            total_contributions=250,
            current_streak=3,
            longest_streak=5,
            contributions_today=1,
        )
        evo = determine_evolution(act)
        frames, hero = generate_walking_animation(
            evolution=evo,
            canvas_width=400,
            canvas_height=70,
            background="transparent",
            steps_per_direction=8,
        )
        # 8 right + 1 turn + 8 left + 1 turn = 18 frames
        self.assertEqual(len(frames), 18)
        self.assertEqual(frames[0].size, (400, 70))
        self.assertEqual(hero.mode, "RGBA")

    def test_save_kiko_outputs(self):
        act = AccountActivity(
            username="testuser",
            total_contributions=250,
            current_streak=3,
            longest_streak=5,
            contributions_today=1,
        )
        evo = determine_evolution(act)
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = save_kiko_outputs(
                activity=act,
                evolution=evo,
                output_dir=tmpdir,
                canvas_width=400,
                canvas_height=70,
                background="dark",
            )
            self.assertTrue(os.path.exists(outputs["gif"]))
            self.assertTrue(os.path.exists(outputs["png"]))
            self.assertTrue(os.path.exists(outputs["preview"]))
            
            # Verify gif is readable by PIL
            with Image.open(outputs["gif"]) as im:
                self.assertTrue(im.is_animated)
                self.assertGreater(im.n_frames, 1)


if __name__ == "__main__":
    unittest.main()
