"""Local BM25-style keyword baseline, NOT a semantic answer validator."""

from collections import Counter
from math import log
import re
import unicodedata

from .sources import in_scope, allows_passage_answer

STOP_WORDS = set("a an the is are can i my of to in it do and when what how many at on for with you your does did be as from this that have has happens happen me please about rule rules game next another while".split())
ALIASES = {"sail": "move", "sailing": "move", "construction": "build", "castling": "castle", "castled": "castle", "drawing": "draw", "draws": "draw",
           "building": "build", "built": "build", "settlements": "settlement", "cards": "card",
           "outbreaks": "outbreak", "ships": "ship", "shelters": "shelter",
           "actions": "action", "resources": "resource", "cities": "city", "cubes": "cube",
           "diseases": "disease", "cured": "cure", "curing": "cure", "eradicated": "eradicate",
           "eradication": "eradicate", "played": "play", "playing": "play", "gaining": "gain",
           "requires": "require", "required": "require", "rolling": "roll", "rolled": "roll",
           "intentionally": "intent", "intention": "intent", "touches": "touch", "touched": "touch"}


def tokens(text):
    words = re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower())
    return [ALIASES.get(word, word) for word in words if word not in STOP_WORDS and len(word) > 1]


def _rank(question, game, edition, passages, limit=6):
    query_words = tokens(question)
    query_pairs = set(zip(query_words, query_words[1:]))
    query = set(tokens(question))
    # Small, explicit vocabulary hints; this is still lexical search, not AI.
    lowered = question.lower()
    if game == "catan" and "settlement" in lowered and any(term in lowered for term in ("next to", "adjacent", "distance")):
        query.update({"distance", "adjacent"})
    if game == "dominion" and "end" in lowered and "turn" in lowered:
        query.update({"clean", "up"})
    if query & {"cost", "costs", "pay", "expend"}:
        query.update({"cost", "pay", "expend", "require"})
    scoped = [p for p in passages if in_scope(p, game, edition)]
    if game == "chess":
        verified = [p for p in scoped if allows_passage_answer(p)]
        if verified:
            scoped = verified
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
            words = tokens(passage["text"])
            pairs = set(zip(words, words[1:]))
            score += 2 * len(query_pairs & pairs)
            if query & {"cost", "costs", "pay", "expend"}:
                subjects = set(query_words) - {"cost", "costs", "pay", "expend", "require", "resource", "build", "one"}
                for sentence in re.split(r"[.!?]", passage["text"]):
                    terms = set(tokens(sentence))
                    if terms & {"cost", "costs", "pay", "expend"} and terms & subjects:
                        score += 5
                        break
            # Count questions need the allowance/limit, not a worked example
            # or a turn-order chart repeating the same action count.
            if "how many" in lowered:
                subjects = set(query_words) - {"take", "during", "part", "turn", "normally", "normal", "each"}
                for sentence in re.split(r"[.!?]", passage["text"]):
                    if re.search(r"\b(?:up to|at most|at least|no more than)\s+\d+", sentence, re.I) and subjects & set(tokens(sentence)):
                        score += 8
                        break
            ranked.append((score, passage))
    ranked.sort(key=lambda item: item[0], reverse=True)
    selected = []
    while ranked and len(selected) < limit:
        def diversified(item):
            score, passage = item
            repeated_page = any(p["source_id"] == passage["source_id"] and p.get("page") == passage.get("page") for p in selected)
            return score * (.65 if repeated_page else 1)
        best = max(ranked, key=diversified)
        selected.append(best[1])
        ranked.remove(best)
    return selected


def retrieve(question, game, edition, passages, limit=6):
    # Reserve evidence for each explicit subquestion instead of letting the
    # longest clause consume the whole context. This never uses the answer key.
    clauses = re.split(r"\band\s+(?=(?:may|can|how|what|does|do|is|are|must|should)\b)",
                       question, flags=re.IGNORECASE)
    selected = []
    if len(clauses) > 1:
        objects = set(tokens(clauses[0])) & {"ship", "road", "settlement", "city", "pawn", "king", "queen", "disease", "card"}
        for index, clause in enumerate(clauses[:3]):
            # Only resolve a search pronoun when the first clause names exactly
            # one supported object; never change the question sent to the model.
            if index and len(objects) == 1:
                clause = re.sub(r"\bit\b", next(iter(objects)), clause, flags=re.IGNORECASE)
            for passage in _rank(clause, game, edition, passages, limit=2):
                if passage not in selected and len(selected) < limit:
                    selected.append(passage)
    for passage in _rank(question, game, edition, passages, limit=limit):
        if passage not in selected and len(selected) < limit:
            selected.append(passage)
    if game == "catan" and edition != "base-5" and "settlement" in tokens(question):
        # Expansion excerpts may reference a base rule without defining it.
        if any("distance" in tokens(p["text"]) for p in selected):
            base = _rank("distance rule adjacent intersections vacant settlement city", game, "base-5", passages, limit=1)
            if base and base[0] not in selected:
                selected = selected[:max(0, limit-1)] + base
    return selected
