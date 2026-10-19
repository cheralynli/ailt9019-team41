"""Local BM25-style keyword baseline, NOT a semantic answer validator."""

from collections import Counter
from math import log
import re
import unicodedata

from .sources import in_scope

STOP_WORDS = set("a an the is are can i my of to in it do and when what how many at on for with you your does did be as from this that have has happens happen me please about rule rules game next another while".split())
ALIASES = {"castling": "castle", "castled": "castle", "drawing": "draw", "draws": "draw",
           "building": "build", "built": "build", "settlements": "settlement", "cards": "card",
           "outbreaks": "outbreak", "ships": "ship", "shelters": "shelter"}


def tokens(text):
    words = re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower())
    return [ALIASES.get(word, word) for word in words if word not in STOP_WORDS and len(word) > 1]


def retrieve(question, game, edition, passages, limit=3):
    query = set(tokens(question))
    # Small, explicit vocabulary hints; this is still lexical search, not AI.
    lowered = question.lower()
    if game == "catan" and "settlement" in lowered and any(term in lowered for term in ("next to", "adjacent", "distance")):
        query.update({"distance", "adjacent"})
    if game == "dominion" and "end" in lowered and "turn" in lowered:
        query.update({"clean", "up"})
    scoped = [p for p in passages if in_scope(p, game, edition)]
    if not query or not scoped:
        return []
    counts = [Counter(tokens(p["text"])) for p in scoped]
    average_length = sum(sum(c.values()) for c in counts) / len(counts) or 1
    frequencies = {word: sum(word in c for c in counts) for word in query}
    ranked = []
    for passage, count in zip(scoped, counts):
        if game == "chess" and "chess960" in passage["text"].lower() and "chess960" not in lowered:
            continue
        score = 0
        for word in query:
            frequency = count[word]
            if frequency:
                rarity = log(1 + (len(scoped) - frequencies[word] + .5) / (frequencies[word] + .5))
                score += rarity * frequency * 2.5 / (frequency + 1.5 * (.25 + .75 * sum(count.values()) / average_length))
        if score:
            ranked.append((score, passage))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [passage for _, passage in ranked[:limit]]
