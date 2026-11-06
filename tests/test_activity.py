import unittest
from unittest.mock import MagicMock, patch
import json

from kiko_profile.activity import fetch_github_activity, AccountActivity, _fetch_via_graphql


class TestActivityFetcher(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_fetch_via_graphql_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_data = {
            "data": {
                "user": {
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "totalContributions": 482,
                            "weeks": [
                                {
                                    "contributionDays": [
                                        {"contributionCount": 2, "date": "2026-11-05"},
                                        {"contributionCount": 4, "date": "2026-11-06"},
                                    ]
                                }
                            ]
                        }
                    },
                    "repositories": {
                        "nodes": [
                            {"primaryLanguage": {"name": "Python", "color": "#3572A5"}},
                            {"primaryLanguage": {"name": "Rust", "color": "#dea584"}},
                            {"primaryLanguage": {"name": "Python", "color": "#3572A5"}},
                        ]
                    }
                }
            }
        }
        mock_resp.read.return_value = json.dumps(mock_data).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = None
        mock_urlopen.return_value = mock_resp

        act = _fetch_via_graphql("testuser", "fake_token")
        self.assertEqual(act.username, "testuser")
        self.assertEqual(act.total_contributions, 482)
        self.assertEqual(act.top_languages[0], "Python")
        self.assertEqual(act.language_colors["Python"], "#3572A5")


if __name__ == "__main__":
    unittest.main()
