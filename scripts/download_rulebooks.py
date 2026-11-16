"""Reproduce the pinned local corpus from official URLs, without redistributing PDFs."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

import httpx

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_HOSTS = {'www.catan.com', 'arbiters.fide.com', 'www.riograndegames.com', 'cdn.svc.asmodee.net'}
MAX_PDF_BYTES = 30 * 1024 * 1024


def download_pdf(url):
    """Download one PDF with the same CA bundle as the project's API client."""
    data = bytearray()
    with httpx.stream(
        'GET',
        url,
        headers={'User-Agent': 'Team41-course-corpus-setup/1.0'},
        follow_redirects=True,
        timeout=45,
    ) as response:
        response.raise_for_status()
        for chunk in response.iter_bytes():
            data.extend(chunk)
            if len(data) > MAX_PDF_BYTES:
                break
    return bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Verify existing PDFs without network access')
    parser.add_argument(
        '--import-dir',
        type=Path,
        help='Use matching PDFs from this browser-download directory before trying the network',
    )
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/rulebook-sources.json').read_text())
    destination = ROOT / 'rulebooks'
    destination.mkdir(exist_ok=True)
    for source in manifest['sources']:
        filename = source['filename']
        if Path(filename).name != filename or not filename.endswith('.pdf'):
            raise ValueError('Invalid source filename')
        path = destination / filename
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
                raise ValueError(f'{filename}: file differs from the pinned corpus. Review it before replacing it.')
            print(f'Verified: {filename}')
            continue
        if args.check_only:
            raise ValueError(f'{filename}: missing local PDF')
        imported = args.import_dir / filename if args.import_dir else None
        if imported and imported.is_file():
            data = imported.read_bytes()
            origin = f'imported from {imported}'
        else:
            parsed = urlsplit(source['download_url'])
            if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS:
                raise ValueError('Source URL is not an allowlisted official download')
            try:
                data = download_pdf(source['download_url'])
                origin = 'downloaded'
            except httpx.HTTPStatusError as error:
                if error.response.status_code == 403:
                    raise RuntimeError(
                        f'{filename}: the publisher blocked automated download (HTTP 403). '
                        f'Download it in a browser from {source["download_url"]}, then run '
                        f'python scripts/download_rulebooks.py --import-dir PATH_TO_DOWNLOADS. '
                        f'The script will verify the file before using it.'
                    ) from error
                raise
        if len(data) > MAX_PDF_BYTES or not data.startswith(b'%PDF-'):
            raise ValueError(f'{filename}: download is not a valid PDF within the size limit')
        if hashlib.sha256(data).hexdigest() != source['sha256']:
            raise ValueError(f'{filename}: publisher file changed. Review its version before updating the manifest.')
        temporary = path.with_suffix('.pdf.tmp')
        temporary.write_bytes(data)
        temporary.replace(path)
        print(f'Verified and saved ({origin}): {filename}')
    print('All six source files match the pinned corpus. Next: python -m referee.indexer')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        raise SystemExit(f'Corpus setup failed: {error}')
