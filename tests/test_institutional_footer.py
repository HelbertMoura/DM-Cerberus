import unittest
from html.parser import HTMLParser
from engine.server import UI_HTML, _render_login_html, _render_setup_2fa_html

class FooterTests(unittest.TestCase):
    def test_shared_content_on_all_three_surfaces(self):
        pages = [UI_HTML, _render_login_html(), _render_setup_2fa_html('TEST', 'TEST', '<svg></svg>')]
        for page in pages:
            with self.subTest(page=page[:30]):
                for text in (
                    'Dev Maniac\'s Systems', 'GitHub', 'Website', 'Apoiar',
                    'Redes e contatos', 'footer-privacy', 'footer-terms', 'footer-lgpd'
                ):
                    self.assertIn(text, page)
                ids = []
                class Parser(HTMLParser):
                    def handle_starttag(self, tag, attrs):
                        ids.extend(v for k, v in attrs if k == 'id')
                Parser().feed(page)
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(1, page.count('<footer class="institutional-footer"'))
                self.assertIn('mailto:contato@devmaniacs.com.br', page)
                self.assertIn('method="dialog"', page)

if __name__ == '__main__':
    unittest.main()
