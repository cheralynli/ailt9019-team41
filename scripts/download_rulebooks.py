"""Reproduce the pinned local corpus from official URLs, without redistributing PDFs."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_HOSTS = {'www.catan.com', 'arbiters.fide.com', 'www.riograndegames.com', 'cdn.svc.asmodee.net'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Verify existing PDFs without network access')
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
        parsed = urlsplit(source['download_url'])
        if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError('Source URL is not an allowlisted official download')
        request = Request(source['download_url'], headers={'User-Agent': 'Team41-course-corpus-setup/1.0'})
        with urlopen(request, timeout=45) as response:
            data = response.read(30 * 1024 * 1024 + 1)
        if len(data) > 30 * 1024 * 1024 or not data.startswith(b'%PDF-'):
            raise ValueError(f'{filename}: download is not a valid PDF within the size limit')
        if hashlib.sha256(data).hexdigest() != source['sha256']:
            raise ValueError(f'{filename}: publisher file changed. Review its version before updating the manifest.')
        temporary = path.with_suffix('.pdf.tmp')
        temporary.write_bytes(data)
        temporary.replace(path)
        print(f'Downloaded and verified: {filename}')
    print('All six source files match the pinned corpus. Next: python -m referee.indexer')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        raise SystemExit(f'Corpus setup failed: {error}')
