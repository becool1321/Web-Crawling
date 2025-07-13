import unittest
from unittest.mock import patch
from crawling import WebCrawler

class TestWebCrawler(unittest.TestCase):

    def setUp(self):
        self.url = "http://example.com"
        self.depth = 2
        self.crawler = WebCrawler(self.url, self.depth)

    def test_normalize_url(self):
        self.assertEqual(self.crawler.normalize_url("  http://test.com  "), "http://test.com")
        self.assertIsNone(self.crawler.normalize_url(None))

    def test_is_same_domain(self):
        self.assertTrue(self.crawler.is_same_domain("http://example.com/page"))
        self.assertFalse(self.crawler.is_same_domain("http://other.com"))

    def test_is_subdomain(self):
        self.assertTrue(self.crawler.is_subdomain("http://sub.example.com"))
        self.assertFalse(self.crawler.is_subdomain("http://example.com"))
        self.assertFalse(self.crawler.is_subdomain("http://other.com"))

    def test_extract_links_and_assets_basic(self):
        from bs4 import BeautifulSoup
        html = '''
        <html>
            <head>
                <script src="/script.js"></script>
                <link rel="stylesheet" href="/style.css">
            </head>
            <body>
                <a href="/link">Link</a>
                <img src="/image.png">
                <form action="/submit"></form>
                <!-- This is a comment -->
                user@example.com
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        list(self.crawler.extract_links_and_assets(soup, self.url))

        self.assertIn("http://example.com/script.js", self.crawler.js_files)
        self.assertIn("http://example.com/style.css", self.crawler.css_files)
        self.assertIn("http://example.com/image.png", self.crawler.images)
        self.assertIn("http://example.com/submit", self.crawler.forms)
        self.assertIn("This is a comment", self.crawler.comments)
        self.assertIn("user@example.com", self.crawler.emails)

    def test_run_without_execution(self):
        with patch.object(self.crawler, 'crawl') as mock_crawl, \
             patch('builtins.print'), \
             patch('builtins.open'), \
             patch('datetime.datetime'):
            self.crawler.run()
            mock_crawl.assert_called_once()

if __name__ == '__main__':
    unittest.main()
