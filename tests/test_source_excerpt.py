"""Real-source extractive answers and conservative fallback, without API calls."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from referee.corpus import load_passages
from referee.retrieval import retrieve
from referee.source_excerpt import source_excerpt_answer
from referee.model import generate_answer

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless((ROOT/'data/passages.json').exists(), 'Local indexed PDFs not present')
class SourceExcerptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.passages=load_passages(ROOT/'data/passages.json')
        cls.cases=json.loads((ROOT/'evaluation/cases.v1.json').read_text())['cases']

    def context(self, case_id):
        case=next(c for c in self.cases if c['id']==case_id)
        return case['question'],retrieve(case['question'],case['game'],case['edition'],self.passages)

    def test_every_displayed_rule_is_verbatim_in_an_actual_citation(self):
        for case_id in ('DOM04','PAN05'):
            question,evidence=self.context(case_id)
            result=source_excerpt_answer(question,evidence)
            self.assertEqual(result['answer_method'],'source_excerpt')
            self.assertEqual(result['answer_review']['provider_requests'],0)
            for quote in result['message'].split('\n\n')[1:]:
                self.assertTrue(any(quote[1:-1] in p['text'] for p in result['citations']))
            self.assertTrue(all(p in evidence for p in result['citations']))

    def test_known_extra_claims_cannot_be_appended_by_the_model(self):
        for case_id in ('DOM04','PAN05'):
            question,evidence=self.context(case_id)
            with patch.dict('os.environ',{'COURSE_API_KEY':'synthetic-test-key'},clear=True), \
                 patch('referee.course_api.request_text') as api:
                result=generate_answer(question,evidence)
            api.assert_not_called()
            self.assertEqual(result['status'],'answer')
            self.assertNotIn('Scientist',result['message'])
            self.assertNotIn('only enters play',result['message'])

    def test_missing_required_rule_uses_normal_model_path(self):
        question,evidence=self.context('PAN05')
        incomplete=[p for p in evidence if p['page']!=7]
        self.assertIsNone(source_excerpt_answer(question,incomplete))
        mock=json.dumps({'status':'refusal','message':'Synthetic fallback.','citation_ids':[]})
        with patch.dict('os.environ',{'COURSE_API_KEY':'synthetic-test-key'},clear=True), \
             patch('referee.course_api.request_text',return_value=mock) as api:
            result=generate_answer(question,incomplete)
        api.assert_called_once()
        self.assertEqual(result['message'],'Synthetic fallback.')

    def test_wrong_source_and_missing_metadata_cannot_supply_quotes(self):
        question,evidence=self.context('DOM04')
        for changes in ({'source_id':'unapproved'}, {'id':None}, {'page':None}, {'game':'chess'}):
            altered=[{**p,**changes} for p in evidence]
            self.assertIsNone(source_excerpt_answer(question,altered))

    def test_other_fixed_questions_still_use_existing_path(self):
        matched=[]
        for case in self.cases:
            evidence=retrieve(case['question'],case['game'],case['edition'],self.passages)
            if source_excerpt_answer(case['question'],evidence):matched.append(case['id'])
        self.assertEqual(matched,['DOM04','PAN05'])

    def test_paraphrases_do_not_require_exact_benchmark_question(self):
        for case_id,question in (
            ('DOM04','By default, where does a gained card go, and do I play it right away?'),
            ('PAN05','Have we won with all 4 diseases cured if cubes remain, and what is eradication?'),
        ):
            _,evidence=self.context(case_id)
            self.assertIsNotNone(source_excerpt_answer(question,evidence))
