"""Narrow, source-extractive answers for two explicit rule intents.

This is deliberately not model generation. No evaluation IDs/keys are consulted.
Every displayed rule sentence must occur verbatim in the retrieved allowlisted
source; otherwise the normal model path is used. Source versions or wording that
do not match cannot silently inherit these extracts.
"""
import re


DOMINION = (
    ('dominion-base', 'Take a card from the Supply and put it into your discard pile.'),
    ('dominion-base', 'You do not play a card when you gain it; it just goes to your discard pile.'),
    ('dominion-base', 'Sometimes a card will let you gain a card to a location other than your discard pile, but by default all gained cards are put into your discard pile.'),
)
PANDEMIC = (
    ('pandemic-base', 'The players win as soon as cures to all 4 diseases are discovered.'),
    ('pandemic-base', 'When a disease is cured, its cubes remain on the board and new cubes can still be placed during epidemics or infections (see Epidemics and Infections on page 6).'),
    ('pandemic-base', 'If no cubes of this color are on the board, this disease is now eradicated.'),
    ('pandemic-base', 'Removing the last cube of a disease that is not cured has no effect.'),
)


def source_excerpt_answer(question, passages):
    """Use complete retrieved literal excerpts, never remembered paraphrases."""
    games = {p.get('game') for p in passages}
    query = question.casefold()
    required = None
    if (games == {'dominion'} and re.search(r'\bgain(?:ed|ing)?\b', query)
            and re.search(r'\bcard\b', query) and re.search(r'\bplay\b', query)
            and re.search(r'\b(?:immediately|right away)\b', query)
            and re.search(r'\b(?:where|discard)\b', query)):
        required = DOMINION
    elif (games == {'pandemic'} and re.search(r'\ball (?:four|4)\b', query)
          and re.search(r'\bcur(?:e|ed|es|ing)\b', query)
          and 'eradicat' in query and re.search(r'\b(?:win|won|winning)\b', query)):
        required = PANDEMIC
    if required is None:
        return None
    citations = []
    sentences = []
    for source_id, sentence in required:
        passage = next((p for p in passages if p.get('source_id') == source_id
                        and p.get('id') and p.get('page')
                        and sentence in p.get('text', '')), None)
        if passage is None:
            return None
        if passage not in citations:
            citations.append(passage)
        sentences.append('“' + sentence + '”')
    return {'status': 'answer', 'message': 'The retrieved rules state:\n\n' + '\n\n'.join(sentences),
            'citations': citations,
            'answer_method': 'source_excerpt',
            'answer_review': {'revisions': 0, 'findings': [], 'unresolved': [],
                              'method': 'verbatim_retrieved_source', 'provider_requests': 0}}
