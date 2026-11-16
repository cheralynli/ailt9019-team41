import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from scripts.download_rulebooks import MAX_PDF_BYTES, download_pdf, main


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

    def test_import_dir_hash_checks_and_saves_browser_download(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            downloads = root / 'downloads'
            downloads.mkdir()
            data = b'%PDF-browser-download'
            (downloads / 'rules.pdf').write_bytes(data)
            (root / 'docs').mkdir()
            manifest = {'sources': [{
                'filename': 'rules.pdf',
                'download_url': 'https://www.catan.com/rules.pdf',
                'sha256': hashlib.sha256(data).hexdigest(),
            }]}
            (root / 'docs' / 'rulebook-sources.json').write_text(json.dumps(manifest))
            argv = ['download_rulebooks.py', '--import-dir', str(downloads)]
            with patch('scripts.download_rulebooks.ROOT', root), patch.object(sys, 'argv', argv):
                main()
            self.assertEqual((root / 'rulebooks' / 'rules.pdf').read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
