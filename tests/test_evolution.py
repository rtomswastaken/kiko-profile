import unittest
from kiko_profile.activity import AccountActivity
from kiko_profile.evolution import determine_evolution


class TestEvolutionRules(unittest.TestCase):
    def test_stage_selection_by_contributions(self):
        # Baby stage (< 150 contributions)
        act_baby = AccountActivity(
            username="testuser",
            total_contributions=45,
            current_streak=1,
            longest_streak=3,
            contributions_today=0,
        )
        evo_baby = determine_evolution(act_baby)
        self.assertEqual(evo_baby.stage_name, "baby")
        self.assertIn("Baby", evo_baby.stage_title)

        # Juvenile stage (150 - 499 contributions)
        act_juv = AccountActivity(
            username="testuser",
            total_contributions=250,
            current_streak=3,
            longest_streak=10,
            contributions_today=1,
        )
        evo_juv = determine_evolution(act_juv)
        self.assertEqual(evo_juv.stage_name, "juvenile")
        self.assertIn("Juvenile", evo_juv.stage_title)

        # Titan stage (500+ contributions)
        act_titan = AccountActivity(
            username="testuser",
            total_contributions=1200,
            current_streak=7,
            longest_streak=20,
            contributions_today=4,
        )
        evo_titan = determine_evolution(act_titan)
        self.assertEqual(evo_titan.stage_name, "titan")
        self.assertIn("Titan", evo_titan.stage_title)

    def test_forced_stage_override(self):
        act = AccountActivity(
            username="testuser",
            total_contributions=5000,
            current_streak=10,
            longest_streak=30,
            contributions_today=5,
        )
        evo_forced = determine_evolution(act, forced_stage="baby")
        self.assertEqual(evo_forced.stage_name, "baby")

    def test_gait_cadence_adjustments(self):
        # Active today: faster walk speed
        act_active = AccountActivity(
            username="testuser",
            total_contributions=300,
            current_streak=5,
            longest_streak=10,
            contributions_today=2,
        )
        evo_active = determine_evolution(act_active)
        self.assertEqual(evo_active.frame_duration_ms, 55)
        self.assertEqual(evo_active.pace_description, "energetic stride")

        # Quiet day, 0 streak: leisurely amble
        act_quiet = AccountActivity(
            username="testuser",
            total_contributions=300,
            current_streak=0,
            longest_streak=10,
            contributions_today=0,
        )
        evo_quiet = determine_evolution(act_quiet)
        self.assertEqual(evo_quiet.frame_duration_ms, 80)
        self.assertEqual(evo_quiet.pace_description, "leisurely amble")


if __name__ == "__main__":
    unittest.main()
