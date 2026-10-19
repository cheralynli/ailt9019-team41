"""The replaceable request → retrieval → model → result pipeline."""

from .catalog import GAMES
from .model import ModelNotConfigured, generate_answer
from .retrieval import retrieve
from .sources import in_scope


def result(status, message):
    return {"status": status, "message": message, "citations": []}


def answer_question(payload, passages):
    if not isinstance(payload, dict):
        raise ValueError("Send a JSON object with a game, ruleset and question.")
    game, edition, question = (payload.get(key) for key in ("game", "edition", "question"))
    if not all(isinstance(value, str) for value in (game, edition, question)):
        raise ValueError("Choose a game and ruleset, then enter a question.")
    question = question.strip()
    if not question or len(question) > 2000:
        raise ValueError("Enter a question between 1 and 2,000 characters.")
    selected = next((item for item in GAMES if item["id"] == game), None)
    if selected is None or edition not in {item["id"] for item in selected["editions"]}:
        return result("unsupported", "That game or ruleset is outside the planned collection. Please select one from the menu.")
    if not any(in_scope(p, game, edition) for p in passages):
        return result("not_ready", "The website and Python backend are connected, but this rulebook has not been indexed yet. The AI model is also not connected. No ruling or citation has been generated.")
    evidence = retrieve(question, game, edition, passages)
    if not evidence:
        return result("no_evidence", "The starter search found no matching passage. I cannot provide a supported ruling. Try a more specific rules question.")
    try:
        return generate_answer(question, evidence)
    except ModelNotConfigured:
        return {"status": "search_only", "message": "Here are matching excerpts from your local rulebooks. These are keyword-search results, not an AI ruling. Check the original pages for context; diagrams and formatting may not survive extraction. The model API is not connected yet.",
                "citations": evidence}
