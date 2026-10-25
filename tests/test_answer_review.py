"""Observed error forms and bounded revision flow; all provider calls are mocked."""
import json
import unittest
from unittest.mock import patch
from referee.answer_review import scope_findings
from referee.model import generate_answer

PAN_BAD = [
    'Eradication occurs only when no cubes remain. Once eradicated, no new cubes can be placed in cities of that color.',
    'When eradicated, no new cubes are placed in cities of that color.',
    'When eradicated, no new cubes are placed in cities of that disease color during infection steps.',
    'Eradication occurs only when a cured disease has no cubes left on the board, which prevents new cubes from being placed in cities of that color during infections.',
]
DOM_BAD = 'A gained card only enters your hand or gets played if a specific card effect instructs you to do so.'


class ScopeCheckTests(unittest.TestCase):
    def test_all_observed_eradication_wordings_are_flagged(self):
        for message in PAN_BAD:
            with self.subTest(message=message):
                self.assertEqual(scope_findings(message, [{'game': 'pandemic'}]), ['eradication_city_scope'])

    def test_disease_cube_scope_is_not_confused_with_city_scope(self):
        for message in (
            'An eradicated disease has no cubes remaining. No more cubes of that disease color are placed.',
            'Once eradicated, no new cubes of that disease color are placed in cities of that color.',
            'Once eradicated, no new cubes of that disease color are placed in cities of that disease color.',
            'An eradicated disease has no cubes remaining. Other colors may still spread into those cities.',
        ):
            self.assertEqual(scope_findings(message, [{'game': 'pandemic'}]), [])

    def test_gain_event_exception_does_not_restrict_future_draw_or_play(self):
        self.assertEqual(scope_findings(DOM_BAD, [{'game': 'dominion'}]), ['gain_future_scope'])
        for message in (
            'When you gain a card, it goes to your discard pile. You do not play it immediately.',
            'A gained card only enters your hand immediately if a specific card effect instructs it.',
            'A gained card only enters your hand directly if a specific effect instructs it.',
        ):
            self.assertEqual(scope_findings(message, [{'game': 'dominion'}]), [])

    def test_checks_do_not_apply_to_other_or_mixed_games(self):
        for passages in ([{'game':'chess'}], [{'game':'pandemic'}, {'game':'dominion'}]):
            self.assertEqual(scope_findings('Eradication: '+PAN_BAD[1]+' '+DOM_BAD, passages), [])


@patch.dict('os.environ', {'COURSE_API_KEY':'synthetic-test-key'}, clear=True)
class RevisionTests(unittest.TestCase):
    passages = [{'game':'pandemic', 'text':'Synthetic evidence fixture', 'id':'synthetic-source', 'page':1}]

    @staticmethod
    def answer(message, ids=None):
        return json.dumps({'status':'answer', 'message':message, 'citation_ids':ids if ids is not None else ['P1']})

    def test_one_grounded_revision_replaces_bad_draft_not_local_citations(self):
        safe = 'A cured disease is eradicated when no cubes of its color remain.'
        with patch('referee.course_api.request_text', side_effect=[self.answer(PAN_BAD[2]), self.answer(safe)]) as api:
            result = generate_answer('Compare cure and eradication.', self.passages)
        self.assertEqual(api.call_count,2)
        self.assertEqual(result['message'],safe)
        self.assertEqual(result['citations'],self.passages)
        self.assertEqual(result['answer_review']['revisions'],1)
        revision_payload = api.call_args.args[1]
        self.assertEqual(revision_payload['question'],'Compare cure and eradication.')
        self.assertEqual(revision_payload['evidence'][0]['text'],self.passages[0]['text'])
        self.assertIn('draft',revision_payload)
        self.assertNotIn('synthetic-test-key',json.dumps(revision_payload))

    def test_dominion_revision_preserves_immediate_scope(self):
        passages=[{**self.passages[0],'game':'dominion'}]
        safe='When you gain a card, it normally goes to your discard pile. You do not play it immediately.'
        with patch('referee.course_api.request_text', side_effect=[self.answer(DOM_BAD),self.answer(safe)]) as api:
            result=generate_answer('Where does a gained card go?',passages)
        self.assertEqual(api.call_count,2)
        self.assertEqual(result['status'],'answer')
        self.assertEqual(result['answer_review']['findings'],['gain_future_scope'])

    def test_persistent_error_is_not_displayed_and_does_not_loop(self):
        with patch('referee.course_api.request_text', return_value=self.answer(PAN_BAD[1])) as api:
            result=generate_answer('Compare cure and eradication.',self.passages)
        self.assertEqual(api.call_count,2)
        self.assertEqual(result['status'],'refusal')
        self.assertEqual(result['diagnostic'],'answer_scope_unresolved')
        self.assertEqual(result['citations'],[])
        self.assertNotIn('cities of that color',result['message'])

    def test_revised_citations_are_validated_again(self):
        with patch('referee.course_api.request_text', side_effect=[self.answer(PAN_BAD[1]),self.answer('Corrected text',['invented'])]) as api:
            result=generate_answer('Compare cure and eradication.',self.passages)
        self.assertEqual(api.call_count,2)
        self.assertEqual(result['diagnostic'],'invalid_model_output')
        self.assertEqual(result['citations'],[])

    def test_revision_transport_failure_is_not_retried_or_exposed(self):
        with patch('referee.course_api.request_text', side_effect=[self.answer(PAN_BAD[1]),TimeoutError('synthetic-test-key')]) as api:
            result=generate_answer('Compare cure and eradication.',self.passages)
        self.assertEqual(api.call_count,2)
        self.assertEqual(result['diagnostic'],'timeout')
        self.assertNotIn('synthetic-test-key',json.dumps(result))

    def test_focused_answer_and_refusal_need_only_one_call(self):
        for raw in (self.answer('Cured and eradicated are distinct states.'),
                    json.dumps({'status':'refusal','message':'No evidence.','citation_ids':[]})):
            with patch('referee.course_api.request_text',return_value=raw) as api:
                result=generate_answer('fixture question',self.passages)
            self.assertEqual(api.call_count,1)
            self.assertNotIn('answer_review',result)
