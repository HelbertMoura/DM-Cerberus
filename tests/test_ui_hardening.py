"""Regression contracts for the solid Inspector UI and defensive JavaScript."""

import re
import shutil
import subprocess
import unittest

from engine.server import UI_HTML, _render_login_html, _render_setup_2fa_html


class SolidInspectorUIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pages = {
            "dashboard": UI_HTML,
            "login": _render_login_html(),
            "setup_2fa": _render_setup_2fa_html("JBSWY3DPEHPK3PXP", "otpauth://totp/test", "<svg></svg>"),
        }

    def test_all_pages_use_only_solid_industrial_surfaces(self) -> None:
        forbidden = (
            "radial-gradient", "linear-gradient", "conic-gradient",
            "backdrop-filter", "blur(", "rgba(", "#8b35d1",
            "--dm-purple", "purple",
        )
        for page_name, html in self.pages.items():
            lowered = html.lower()
            for token in forbidden:
                with self.subTest(page=page_name, token=token):
                    self.assertNotIn(token, lowered)

    def test_all_pages_expose_brand_palette_fonts_and_44px_controls(self) -> None:
        for page_name, html in self.pages.items():
            lowered = html.lower()
            for color in ("#061637", "#0a192f", "#0d2247", "#1e3a6d", "#08b9ca", "#ff4c4c", "#ffc529", "#1e40af"):
                with self.subTest(page=page_name, color=color):
                    self.assertIn(color, lowered)
            for font in ("space grotesk", "inter", "ibm plex mono"):
                with self.subTest(page=page_name, font=font):
                    self.assertIn(font, lowered)
            self.assertRegex(lowered, r"min-height:\s*(?:44|4[5-9])px")

    def test_dashboard_has_isolated_initializers_and_required_interactions(self) -> None:
        for initializer in (
            "initTabs", "initTopologyCanvas", "initMetrics", "initSearch",
            "initInbox", "initModals", "initReindex",
        ):
            with self.subTest(initializer=initializer):
                self.assertIn("function " + initializer + "()", UI_HTML)
        self.assertIn('document.addEventListener("DOMContentLoaded"', UI_HTML)
        self.assertIn('e.key === "Enter"', UI_HTML)
        self.assertIn('querySelectorAll(".chip")', UI_HTML)
        self.assertIn('result-card-open', UI_HTML)
        self.assertIn('verify-candidate-btn', UI_HTML)
        self.assertIn('/verify', UI_HTML)
        self.assertIn('/promote', UI_HTML)
        self.assertIn('/reject', UI_HTML)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for JavaScript syntax validation")
    def test_dashboard_javascript_compiles_in_real_javascript_engine(self) -> None:
        scripts = re.findall(r"<script>(.*?)</script>", UI_HTML, flags=re.DOTALL)
        self.assertEqual(1, len(scripts))
        result = subprocess.run(
            ["node", "-e", "new Function(require('fs').readFileSync(0, 'utf8'));"],
            input=scripts[0], text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
