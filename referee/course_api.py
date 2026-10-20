"""Course Bailian Token Plan adapter; one in-flight request per server process."""
import json
import os
from threading import BoundedSemaphore
import httpx

BASE_URL = 'https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1'
DEFAULT_MODEL = 'qwen3.8-flash'
_SLOT = BoundedSemaphore(1)


class CourseBusy(Exception):
    pass


def request_text(system, payload):
    if not _SLOT.acquire(blocking=False):
        raise CourseBusy()
    try:
        body = {'model': os.environ.get('COURSE_MODEL', DEFAULT_MODEL),
                'messages': [{'role': 'system', 'content': system},
                             {'role': 'user', 'content': json.dumps(payload)}],
                'response_format': {'type': 'json_object'},
                'temperature': 0, 'max_tokens': 2048, 'stream': False,
                'enable_thinking': False}
        with httpx.Client(timeout=45, follow_redirects=False) as client:
            response = client.post(BASE_URL + '/chat/completions',
                                   headers={'Authorization': 'Bearer ' + os.environ['COURSE_API_KEY']},
                                   json=body)
            response.raise_for_status()
            data = response.json()
        choice = data['choices'][0]
        if choice.get('finish_reason') != 'stop':
            raise ValueError('Incomplete model response')
        text = choice['message']['content']
        if not isinstance(text, str):
            raise ValueError('Missing text response')
        return text
    finally:
        _SLOT.release()
