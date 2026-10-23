"""Pinned-PDF separation and scoring regression tests, without live API calls."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from referee.chess import extract_chess, verified_passage
from referee.sources import allows_passage_answer
from referee.corpus import load_passages
from referee.pipeline import answer_question
from referee.evaluation import load_cases, check_references, score_rows
from referee.retrieval import retrieve

ROOT = Path(__file__).resolve().parents[1]


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.cases, _ = load_cases(ROOT / 'evaluation/cases.v1.json')

    def rows(self):
        return [dict(id=c['id'], ruling_correct='yes', citation_correct='yes', refusal_correct='yes') for c in self.cases]

    def test_unreviewed_rows_never_pass(self):
        rows = [dict(id=c['id']) for c in self.cases]
        score = score_rows(rows, self.cases)
        self.assertFalse(score['passed'])
        self.assertFalse(score['complete'])
        self.assertEqual(len(score['pending_cases']), 32)

    def test_thresholds_and_separate_denominators(self):
        rows = self.rows()
        answered = [i for i, c in enumerate(self.cases) if c['category'] != 'refusal']
        for i in answered[:5]:rows[i]['ruling_correct'] = 'no'
        for i in answered[:2]:rows[i]['citation_correct'] = 'no'
        result = score_rows(rows, self.cases)
        self.assertEqual((result['ruling_correct'], result['citation_correct'], result['refusals_correct']), (21,24,6))
        self.assertTrue(result['passed'])
        rows[answered[2]]['citation_correct'] = 'no'
        self.assertFalse(score_rows(rows, self.cases)['passed'])

    def test_each_refusal_is_required(self):
        rows = self.rows()
        idx = next(i for i,c in enumerate(self.cases) if c['category'] == 'refusal')
        rows[idx]['refusal_correct'] = 'no'
        self.assertFalse(score_rows(rows,self.cases)['passed'])

    def test_missing_or_duplicate_cases_rejected(self):
        for rows in (self.rows()[:-1], self.rows()[:-1]+[self.rows()[0]]):
            with self.assertRaises(ValueError):score_rows(rows,self.cases)

    def test_suite_changes_require_a_new_frozen_version(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'cases.v1.json'
            path.write_text((ROOT/'evaluation/cases.v1.json').read_text()+' ')
            path.with_suffix('.sha256').write_text((ROOT/'evaluation/cases.v1.sha256').read_text())
            with self.assertRaises(ValueError):load_cases(path)


@unittest.skipUnless((ROOT/'rulebooks/Arbiters_Manual_2025.pdf').exists(), 'Pinned local Chess PDF not present')
class ChessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.passages, cls.audit = extract_chess(ROOT/'rulebooks/Arbiters_Manual_2025.pdf')

    def test_all_52_pages_are_classified(self):
        self.assertEqual([x['pdf_page'] for x in self.audit],list(range(16,68)))
        self.assertTrue(all(p['page'] <= 56 for p in self.passages if p['kind']=='official_law'))

    def test_commentary_excluded_and_original_encoding_preserved(self):
        law = ' '.join(p['text'] for p in self.passages if p['page']==37 and p['kind']=='official_law')
        comment = ' '.join(p['text'] for p in self.passages if p['page']==37 and p['kind']=='arbiter_commentary')
        self.assertIn('player’s king',law)
        self.assertNotIn('The player is forfeited',law)
        self.assertIn('The player is forfeited',comment)

    def test_verified_law_can_reach_the_model(self):
        passage = next(p for p in self.passages if p['page']==24 and p['kind']=='official_law')
        self.assertTrue(allows_passage_answer(passage))
        with patch('referee.pipeline.generate_answer', return_value={'status':'answer','message':'Synthetic mock','citations':[passage]}) as model:
            result = answer_question({'game':'chess','edition':'laws-2023','question':'Can I castle while my king is in check?'},[passage])
        self.assertEqual(result['status'],'answer')
        model.assert_called_once()

    def test_tampered_text_and_non_law_never_enable_answers(self):
        law = next(p for p in self.passages if p['kind']=='official_law')
        self.assertIsNone(verified_passage({**law,'text':law['text']+' invented text'}))
        for kind in ('arbiter_commentary','non_law_guidance','reference_glossary'):
            p = next(p for p in self.passages if p['kind']==kind)
            self.assertFalse(allows_passage_answer({**p,'kind':'official_law'}))

    def test_unknown_pdf_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'unknown.pdf';path.write_bytes(b'not the pinned PDF')
            with self.assertRaises(ValueError):extract_chess(path)

    def test_reference_anchors_match_original_rulebooks(self):
        cases,_=load_cases(ROOT/'evaluation/cases.v1.json')
        check_references(cases,ROOT)


@unittest.skipUnless((ROOT/'data/passages.json').exists(), 'Local indexed rulebooks not present')
class LiveFailureRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.passages = load_passages(ROOT/'data/passages.json')

    def test_ship_cost_and_move_conditions_are_both_supplied(self):
        for question in (
            'What resources does a ship cost, and may I move that ship on the same turn I built it?',
            'What does a ship cost, and can it sail immediately after construction?',
        ):
            evidence = retrieve(question, 'catan', 'seafarers-5', self.passages)
            self.assertTrue(any(p['source_id']=='catan-seafarers' and p['page']==3
                                and '1 wool' in p['text'] and '1 lumber' in p['text'] for p in evidence))
            self.assertTrue(any(p['source_id']=='catan-seafarers' and p['page']==4
                                and 'same turn' in p['text'] for p in evidence))
            self.assertLessEqual(len(evidence),6)

    def test_composite_search_stays_in_selected_ruleset(self):
        evidence = retrieve('What does a ship cost, and can I move it now?',
                            'catan', 'base-5', self.passages)
        self.assertTrue(all(p['source_id']=='catan-base' for p in evidence))

    def test_expansion_distance_reference_includes_base_definition(self):
        evidence = retrieve('May I build a settlement on a new island reached by my shipping route?',
                            'catan', 'seafarers-5', self.passages)
        self.assertTrue(any(p['source_id']=='catan-base' and 'adjacent intersections' in p['text']
                            for p in evidence))
        self.assertLessEqual(len(evidence),6)
