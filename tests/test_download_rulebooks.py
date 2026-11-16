import unittest
from unittest.mock import patch

import httpx

from scripts.download_rulebooks import MAX_PDF_BYTES, download_pdf


class DownloadTests(unittest.TestCase):
    def test_download_uses_verified_http_client_and_returns_pdf(self):
        response = httpx.Response(
            200,
            content=b'%PDF-test',
            request=httpx.Request('GET', 'https://www.catan.com/rules.pdf'),
        )
        context = unittest.mock.MagicMock()
        context.__enter__.return_value = response
        with patch('scripts.download_rulebooks.httpx.stream', return_value=context) as stream:
            self.assertEqual(download_pdf('https://www.catan.com/rules.pdf'), b'%PDF-test')
        self.assertTrue(stream.call_args.kwargs['follow_redirects'])

    def test_download_stops_after_size_limit(self):
        response = httpx.Response(
            200,
            content=b'x' * (MAX_PDF_BYTES + 1),
            request=httpx.Request('GET', 'https://www.catan.com/rules.pdf'),
        )
        context = unittest.mock.MagicMock()
        context.__enter__.return_value = response
        with patch('scripts.download_rulebooks.httpx.stream', return_value=context):
            self.assertGreater(len(download_pdf('https://www.catan.com/rules.pdf')), MAX_PDF_BYTES)


if __name__ == '__main__':
    unittest.main()
