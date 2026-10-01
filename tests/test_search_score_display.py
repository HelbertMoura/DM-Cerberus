"""Execute the real search row renderer to check visible score precision."""

import json
import re
import shutil
import subprocess
import unittest

from engine.server import UI_HTML


NODE = shutil.which("node")


@unittest.skipUnless(NODE, "Node.js is required for score display validation")
class TestSearchScoreDisplay(unittest.TestCase):
    def render_badges(self, scores):
        renderer = re.search(
            r"var rows = list\.map\(function \(item\) \{(.*?)\}\)\.join\(\"\"\);",
            UI_HTML, re.DOTALL,
        )
        self.assertIsNotNone(renderer, "Search row renderer must be present")
        script = (
            "const fs = require('fs');"
            "const scores = JSON.parse(fs.readFileSync(0, 'utf8'));"
            "const render = new Function('item', 'uiState', 'mode', 'escapeHTML', "
            + json.dumps(renderer.group(1)) + ");"
            "const rows = scores.map(final_score => render("
            "{memory_id: 'fixture', final_score}, {search: {selectedId: ''}},"
            "'lexical', String));"
            "process.stdout.write(JSON.stringify(rows));"
        )
        result = subprocess.run(
            [NODE, "-e", script], input=json.dumps(scores),
            text=True, encoding="utf-8", capture_output=True, check=True, timeout=10,
        )
        badges = []
        for row in json.loads(result.stdout):
            badge = re.search(r'<span class="badge action">([^<]*)</span>', row)
            self.assertIsNotNone(badge, "Rendered row must show its score badge")
            badges.append(badge.group(1))
        return badges

    def test_small_positive_scores_are_visible_and_distinct(self):
        self.assertEqual(
            ["lexical · 1.00e-6", "lexical · 2.00e-6"],
            self.render_badges([0.000001, 0.000002]),
        )

    def test_scientific_format_stops_at_one_hundredth(self):
        self.assertEqual(
            ["lexical · 9.00e-3", "lexical · 0.01"],
            self.render_badges([0.009, 0.01]),
        )

    def test_zero_keeps_two_decimal_places(self):
        self.assertEqual(["lexical · 0.00"], self.render_badges([0]))

    def test_large_score_keeps_two_decimal_places(self):
        self.assertEqual(["lexical · 15.00"], self.render_badges([15]))


if __name__ == "__main__":
    unittest.main()
