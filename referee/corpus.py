"""Load the generated index and reject malformed provenance."""

import json
from .sources import SOURCE_BY_ID, allows_ai_answer


def load_passages(path):
    if not path.exists():
        return []
    passages = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(passages, list):
        raise ValueError("Index must be a list.")
    ids = set()
    for passage in passages:
        if not isinstance(passage, dict):
            raise ValueError("Invalid passage.")
        source = SOURCE_BY_ID.get(passage.get("source_id"))
        if (source is None or not isinstance(passage.get("id"), str)
                or passage["id"] in ids or not isinstance(passage.get("text"), str)
                or not passage["text"].strip() or type(passage.get("page")) is not int):
            raise ValueError("Invalid passage metadata.")
        if (passage.get("game") != source["game"] or passage.get("edition") != source["edition"]
                or not source["pages"][0] <= passage["page"] <= source["pages"][1]):
            raise ValueError("Passage source does not match the approved collection.")
        ids.add(passage["id"])
        # Display metadata comes from the allowlist, not arbitrary index strings.
        passage.update(document=source["document"], edition_label=source["edition_label"],
                       warning=source.get("warning", ""),
                       kind="rulebook_excerpt" if allows_ai_answer(source["id"]) else "rules_and_commentary_unseparated",
                       source_url=f"/api/sources/{source['id']}#page={passage['page']}")
    return passages
