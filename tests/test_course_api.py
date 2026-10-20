"""Course API contract tests. No real key or network requests."""
import json
import unittest
from unittest.mock import patch
import httpx
from referee.model import generate_answer, ModelNotConfigured
from referee.course_api import BASE_URL, _SLOT


@patch.dict('os.environ', {'COURSE_API_KEY': 'test-course-secret',
                           'COURSE_MODEL': 'qwen3.8-flash'}, clear=True)
class CourseTests(unittest.TestCase):
    passages = [{'text': 'Synthetic rule fixture', 'game': 'test', 'page': 2}]

    def call(self, data=None, status=200, finish='stop', body=None):
        request = httpx.Request('POST', BASE_URL + '/chat/completions')
        response = httpx.Response(status, request=request, json=body if body is not None else {
            'choices': [{'finish_reason': finish, 'message': {'content': json.dumps(data)}}]})
        with patch('referee.course_api.httpx.Client') as factory:
            post = factory.return_value.__enter__.return_value.post
            post.return_value = response
            result = generate_answer('fixture question', self.passages)
            self.last_call = post.call_args
        return result

    def test_course_request_and_local_citations(self):
        result = self.call({'status': 'answer', 'message': 'Explanation', 'citation_ids': ['P1']})
        self.assertEqual(result['citations'], self.passages)
        self.assertEqual(self.last_call.args[0], BASE_URL + '/chat/completions')
        body = self.last_call.kwargs['json']
        self.assertEqual(body['model'], 'qwen3.8-flash')
        self.assertFalse(body['enable_thinking'])
        self.assertEqual(body['response_format'], {'type': 'json_object'})
        self.assertNotIn('test-course-secret', json.dumps(body))

    def test_invalid_citation_is_rejected(self):
        self.assertEqual(self.call({'status': 'answer', 'message': 'Text', 'citation_ids': ['invented']})['diagnostic'], 'invalid_model_output')

    def test_refusal_has_no_citations(self):
        self.assertEqual(self.call({'status': 'refusal', 'message': 'Cannot answer', 'citation_ids': []})['status'], 'refusal')

    def test_status_errors_hide_provider_response(self):
        for status, diagnostic in [(400, 'http_400'), (401, 'http_access_denied'), (404, 'http_404'), (429, 'http_429'), (503, 'http_503')]:
            with self.subTest(status=status):
                result = self.call(status=status, body={'error': 'test-course-secret'})
                self.assertEqual(result['diagnostic'], diagnostic)
                self.assertNotIn('test-course-secret', json.dumps(result))

    def test_invalid_envelope_and_truncated_output(self):
        self.assertEqual(self.call(body={})['diagnostic'], 'invalid_model_output')
        self.assertEqual(self.call(finish='length')['diagnostic'], 'invalid_model_output')
        # Previous failures must have released the request slot.
        self.assertEqual(self.call({'status': 'clarification', 'message': 'Which rule?', 'citation_ids': []})['status'], 'clarification')

    def test_concurrent_call_is_not_sent(self):
        _SLOT.acquire()
        try:
            with patch('referee.course_api.httpx.Client') as client:
                self.assertEqual(generate_answer('fixture', self.passages)['diagnostic'], 'busy')
                client.assert_not_called()
        finally:
            _SLOT.release()

    def test_no_key_uses_local_search_configuration(self):
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ModelNotConfigured):
                generate_answer('fixture', self.passages)
