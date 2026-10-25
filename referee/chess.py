"""Separate text in the pinned 2025 manual; never infer policy from index labels.

Only upright Times New Roman body text on PDF pp.16–56 is treated as law.
Italic/smaller text is commentary. Guidelines pp.57–62 and glossary pp.63–67
are retained for audit but never used as laws. Unknown typography is excluded.
"""
from copy import copy
from functools import lru_cache
import hashlib
from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import ContentStream, NameObject, TextStringObject, ByteStringObject, ArrayObject

ROOT = Path(__file__).resolve().parents[1]
PINNED_SHA256 = '0e199bed153ce908c08bd595a4c5eb4b73e435d6f44f3905d683a1c7124d36ed'
PROFILE = 'fide-2025-laws-upright-v1'


def separated_page(page, reader, keep_laws):
    content = ContentStream(page.get_contents(), reader)
    font, size, stack = None, 0, []
    operations = []
    for operands, operator in content.operations:
        if operator == b'q':
            stack.append((font, size))
        elif operator == b'Q' and stack:
            font, size = stack.pop()
        elif operator == b'Tf':
            resource = page['/Resources']['/Font'].get(operands[0])
            font = str(resource.get_object().get('/BaseFont', '')) if resource else ''
            size = float(operands[1])
        is_law = font in {'/Times New Roman', '/Times New Roman,Bold'} and size >= 11.5
        if operator in {b'Tj', b'TJ', b"'", b'"'} and is_law != keep_laws:
            # Preserve positioning operators and numeric kerning, but remove text.
            operands = [ArrayObject([TextStringObject('') if isinstance(x, (str, bytes)) else x for x in item])
                        if isinstance(item, ArrayObject) else TextStringObject('') if isinstance(item, (str, bytes)) else item
                        for item in operands]
        def original_encoding(item):
            if isinstance(item, ArrayObject):
                return ArrayObject([original_encoding(x) for x in item])
            if isinstance(item, TextStringObject):
                try:
                    return ByteStringObject(item.original_bytes)
                except Exception:
                    if not item:
                        return ByteStringObject(b'')
                    raise ValueError('Unrecognized Chess text encoding')
            return item
        operands = [original_encoding(x) for x in operands]
        operations.append((operands, operator))
    content.operations = operations
    filtered = copy(page)
    filtered[NameObject('/Contents')] = content
    return filtered.extract_text() or ''


def extract_chess(path):
    from .indexer import normalize, chunks
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != PINNED_SHA256:
        raise ValueError('Chess PDF differs from the reviewed manual; extraction must be reviewed before AI use.')
    reader = PdfReader(path)
    passages, audit = [], []
    for page in range(16, 68):
        if page <= 56:
            parts = [('official_law', separated_page(reader.pages[page-1], reader, True)),
                     ('arbiter_commentary', separated_page(reader.pages[page-1], reader, False))]
        else:
            parts = [('non_law_guidance' if page <= 62 else 'reference_glossary', reader.pages[page-1].extract_text() or '')]
        counts = {}
        for kind, text in parts:
            text = normalize(text)
            counts[kind] = len(text)
            if len(text) < 30:
                continue
            for i, chunk in enumerate(chunks(text), 1):
                passages.append({'id': f'chess-laws-p{page}-{kind}-{i}', 'source_id': 'chess-laws',
                                 'game': 'chess', 'edition': 'laws-2023', 'page': page,
                                 'printed_page': str(page-9), 'kind': kind, 'text': chunk,
                                 'extraction_profile': PROFILE})
        audit.append({'pdf_page': page, 'characters_by_class': counts})
    return passages, audit


@lru_cache(maxsize=2)
def _verified(path, modified, size):
    try:
        return {p['id']: p for p in extract_chess(path)[0]}
    except (OSError, ValueError):
        return {}


def verified_passage(passage):
    path = ROOT / 'rulebooks/Arbiters_Manual_2025.pdf'
    try:
        stat = path.stat()
        expected = _verified(str(path), stat.st_mtime_ns, stat.st_size).get(passage.get('id'))
    except OSError:
        return None
    if expected and all(passage.get(k) == expected[k] for k in ('text', 'page', 'source_id', 'game', 'edition')):
        return expected
    return None
