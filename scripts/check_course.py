"""Live connection check using a labelled synthetic fixture, not real game rules."""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from referee.model import generate_answer, ModelNotConfigured

print("Provider: course")
print("Model:", os.environ.get("COURSE_MODEL", "qwen3.8-flash"))
try:
    result = generate_answer('In the synthetic test game, how many tokens does each player start with?', [
        {'game': 'synthetic-test', 'edition': 'test-only', 'document': 'Synthetic API fixture',
         'text': 'In this invented test game, each player starts with exactly three tokens.', 'page': 1}])
except ModelNotConfigured:
    print('Configure the selected provider key and model first.')
    sys.exit(1)
print('Status:', result['status'])
print('Response:', result['message'])
print('Validated citations:', len(result['citations']))
if result.get('diagnostic'):
    print('Diagnostic:', result['diagnostic'])
sys.exit(0 if result['status'] == 'answer' and result['citations'] else 1)
