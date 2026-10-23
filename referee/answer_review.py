"""Narrow checks for observed scope errors, not a semantic correctness validator.

Checks depend on the selected game, never evaluation IDs or expected answers.
They request a single evidence-based revision; they do not rewrite game rules.
"""
import re


FINDINGS = {
    'eradication_city_scope': (
        'The draft describes eradication as preventing new cubes in cities of a color. '
        'This confuses disease-cube color with printed city color. Explain only the '
        'requested cure/eradication distinction using cited evidence. Omit the extra '
        'placement claim when it is not requested. Adding the word disease after cities '
        'does not fix the scope: the restriction must qualify the cubes themselves.'),
    'gain_future_scope': (
        'The draft makes a card-effect requirement apply to all future entry into '
        'hand or play. The question concerns the destination and immediate result '
        'of gaining. Restrict any exception to the gain event itself; do not imply '
        'that ordinary later drawing or playing requires a special card effect. '
        'Use only cited evidence and omit unnecessary claims about later turns.'),
}


def scope_findings(message, passages):
    """Recognize known overbroad forms; absence of a finding is not a pass grade."""
    games = {p.get('game') for p in passages}
    text = message.casefold()
    found = []
    if games == {'pandemic'} and 'eradicat' in text:
        # A color restriction on the cubes themselves is materially different
        # from an unqualified ban on cubes in cities with that printed color.
        for sentence in re.split(r'(?<=[.!?])\s+', text):
            match = re.search(r'(?:no\s+(?:new\s+)?|prevent\w*\s+(?:any\s+)?(?:new\s+)?)'
                              r'(?:disease\s+)?cubes\b(?P<tail>[^.!?]*?)'
                              r'\bcities of (?:that|this|the same|its) (?:disease )?colo[u]?r', sentence)
            if match and not re.search(r'\bcubes? of (?:that|this|the|an?) (?:eradicated )?'
                                       r'disease(?: colo[u]?r)?', match.group(0)):
                found.append('eradication_city_scope')
                break
    if games == {'dominion'}:
        for sentence in re.split(r'(?<=[.!?])\s+', text):
            if not (re.search(r'\bgain\w*\b', sentence) and 'only' in sentence
                    and re.search(r'\b(?:hand|play\w*)\b', sentence)
                    and re.search(r'\b(?:if|when|unless)\b', sentence)
                    and re.search(r'\b(?:effect|instruct\w*)\b', sentence)):
                continue
            immediate = re.search(r'\b(?:immediately|directly|on gaining|upon gaining|on gain|at once)\b'
                                  r'|\bwhen (?:you )?gain\b|\bwhen (?:it|the card) is gained\b'
                                  r'|\bas part of gaining\b|\bat the time of gaining\b', sentence)
            if not immediate:
                found.append('gain_future_scope')
                break
    return found
