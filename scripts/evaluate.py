"""Run the fixed suite sequentially. Never store or print credentials."""
import argparse
import csv
from datetime import datetime, timezone
import getpass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from referee.corpus import load_passages
from referee.evaluation import load_cases, check_references, preflight, score_rows
from referee.pipeline import answer_question

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Use the course API; up to 32 sequential requests')
    parser.add_argument('--score', type=Path, help='Score a completed review CSV without API calls')
    args = parser.parse_args()
    cases, digest = load_cases(ROOT / 'evaluation/cases.v1.json')
    if args.score:
        with args.score.open(newline='') as f:
            print(json.dumps(score_rows(list(csv.DictReader(f)), cases), indent=2))
        return
    check_references(cases, ROOT)
    corpus = ROOT / 'data/passages.json'
    passages = load_passages(corpus)
    if not passages:
        raise ValueError('Build the rulebook index first.')
    if args.live and not os.environ.get('COURSE_API_KEY'):
        os.environ['COURSE_API_KEY'] = getpass.getpass('Course API key (hidden): ').strip()
    if args.live and not os.environ.get('COURSE_API_KEY'):
        raise ValueError('A course API key is required for --live')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder = ROOT / 'evaluation/results' / stamp
    folder.mkdir(parents=True)
    metadata = {'mode': 'live' if args.live else 'retrieval_only', 'started_utc': stamp,
                'suite_sha256': digest, 'corpus_sha256': hashlib.sha256(corpus.read_bytes()).hexdigest(),
                'model': os.environ.get('COURSE_MODEL', 'qwen3.8-flash') if args.live else None,
                'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'working_tree_dirty': bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
                'note': 'Citation validity and retrieval coverage do not establish semantic correctness; explicit reviewer grading is required.'}
    (folder / 'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    rows, evidence = [], []
    for i, case in enumerate(cases, 1):
        item = {'case': case, 'preflight': preflight(case, passages)}
        if args.live:
            item['actual'] = answer_question(case, passages)
        evidence.append(item)
        # Save after every case so partial runs are not lost.
        (folder / 'outputs.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n')
        actual = item.get('actual', {})
        rows.append({'id': case['id'], 'game': case['game'], 'category': case['category'],
                     'question': case['question'], 'expected': case['expected'],
                     'expected_references': json.dumps(case['references']),
                     'actual_status': actual.get('status', 'NOT_RUN'), 'actual_message': actual.get('message', ''),
                     'actual_citations': json.dumps(actual.get('citations', []), ensure_ascii=False),
                     'ruling_correct': '', 'citation_correct': '', 'refusal_correct': '', 'reviewer': '', 'notes': ''})
        with (folder / 'review.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        print(f"{i:02}/32 {case['id']}: {actual.get('status', 'retrieval checked; model NOT run')}", flush=True)
        if args.live and actual.get('diagnostic') in {'http_429', 'http_access_denied', 'http_404'}:
            print('Stopping to protect the shared quota: resolve the API configuration/access issue before rerunning.')
            break
    answerable = [x['preflight'] for x in evidence if x['case']['category'] != 'refusal']
    summary = {'mode': metadata['mode'], 'cases': len(evidence),
               'answerable_reference_coverage': sum(x['reference_coverage'] for x in answerable),
               'answerable_total': 26, 'run_complete': len(evidence) == 32, 'accuracy_scored': False,
               'next': 'Review review.csv against outputs.json and the original sources, then run --score.' if args.live else 'Run --live for actual answers; no model accuracy is measured by this preflight.'}
    (folder / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2));print('Results:', folder)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        raise SystemExit(f'Evaluation stopped: {error}')
