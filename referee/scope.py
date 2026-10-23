"""Conservative checks for explicit scope conflicts and unresolved references.

This is not a complete semantic refusal classifier. Remaining cases go through
retrieval and the evidence-only model prompt.
"""
import re

NAMED_GAMES = ('catan', 'chess', 'dominion', 'pandemic', 'monopoly', 'scrabble', 'uno', 'poker')


def check_question(question, game):
    named = {name for name in NAMED_GAMES if re.search(r'\b' + name + r'\b', question, re.I)}
    if named - {game}:
        return {'status': 'unsupported', 'message':
                'This question names a different or unsupported game. Ask about one game at a time and select its matching ruleset.',
                'citations': []}
    simplified = re.sub(r'[?.!]+$', '', question.strip().lower()).strip()
    vague = {'help', 'what happens', 'what happens next', 'can i build', 'can i move',
             'can i play', 'can i trade', 'is this allowed', 'is that allowed',
             'what about this', 'what about that', 'can i do this', 'can i do that',
             'can i do it', 'what should i do'}
    if simplified in vague:
        return {'status': 'clarification', 'message':
                'Which rule or action do you mean? Describe the pieces or cards and the relevant game situation. Each question is checked independently.',
                'citations': []}
    return None
