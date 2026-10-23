"""Fixed-suite validation, retrieval preflight and explicit reviewer scoring."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from .retrieval import retrieve
from .sources import SOURCE_BY_ID
from .indexer import normalize


def load_cases(path):
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != path.with_suffix('.sha256').read_text().split()[0]:
        raise ValueError('Suite digest changed; create a new version instead of editing a scored baseline.')
    cases = json.loads(path.read_text())['cases']
    if len(cases) != 32 or len({c['id'] for c in cases}) != 32:
        raise ValueError('Expected 32 uniquely named cases')
    if Counter(c['game'] for c in cases) != Counter(dict(catan=8, chess=8, dominion=8, pandemic=8)):
        raise ValueError('Expected eight cases per game')
    if Counter(c['category'] for c in cases) != Counter(dict(ordinary=16, two_passage=6, routing=4, refusal=6)):
        raise ValueError('Case categories differ from the proposal')
    return cases, digest


def check_references(cases, root):
    from pypdf import PdfReader
    readers = {}
    chess_laws = None
    for case in cases:
        if case['category'] != 'refusal' and not case['references']:
            raise ValueError('An answerable case lacks references')
        for ref in case['references']:
            sid = ref['source_id']
            if sid not in readers:
                readers[sid] = PdfReader(Path(root) / 'rulebooks' / SOURCE_BY_ID[sid]['filename'])
            if sid == 'chess-laws':
                if chess_laws is None:
                    from .chess import extract_chess
                    separated, _ = extract_chess(Path(root) / 'rulebooks' / SOURCE_BY_ID[sid]['filename'])
                    chess_laws = separated
                page = ' '.join(p['text'] for p in chess_laws if p['page'] == ref['page'] and p['kind'] == 'official_law')
            else:
                page = normalize(readers[sid].pages[ref['page']-1].extract_text() or '')
            if ref['anchor'].casefold() not in page.casefold():
                raise ValueError(f"Source anchor not found: {case['id']}, {sid}, page {ref['page']}")


def preflight(case, passages):
    found = retrieve(case['question'], case['game'], case['edition'], passages)
    # This only measures location/anchor coverage, never answer correctness.
    covered = [any(p['source_id'] == ref['source_id'] and p['page'] == ref['page']
                   and ref['anchor'].casefold() in p['text'].casefold() for p in found)
               for ref in case['references']]
    return {'id': case['id'], 'category': case['category'],
            'reference_coverage': all(covered) if covered else None,
            'covered_references': covered,
            'retrieved': [{'id': p['id'], 'source_id': p['source_id'], 'page': p['page'], 'kind': p.get('kind')} for p in found]}


def score_rows(rows, cases):
    by_id = {r['id']: r for r in rows}
    if len(rows) != 32 or len(by_id) != 32 or set(by_id) != {c['id'] for c in cases}:
        raise ValueError('Review must contain each of the 32 case IDs exactly once')
    ruling, citations, refusals, pending = 0, 0, 0, []
    for case in cases:
        row = by_id[case['id']]
        fields = ('refusal_correct',) if case['category'] == 'refusal' else ('ruling_correct', 'citation_correct')
        if any(row.get(f, '').strip().lower() not in {'yes', 'no'} for f in fields):
            pending.append(case['id'])
            continue
        if case['category'] == 'refusal':
            refusals += row['refusal_correct'].strip().lower() == 'yes'
        else:
            ruling += row['ruling_correct'].strip().lower() == 'yes'
            citations += row['citation_correct'].strip().lower() == 'yes'
    return {'complete': not pending, 'pending_cases': pending, 'ruling_correct': ruling,
            'ruling_total': 26, 'citation_correct': citations, 'citation_total': 26,
            'refusals_correct': refusals, 'refusal_total': 6,
            'passed': not pending and ruling >= 21 and citations >= 24 and refusals == 6}
