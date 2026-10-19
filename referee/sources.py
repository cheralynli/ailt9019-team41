"""Explicit local source allowlist. Never automatically index arbitrary PDFs."""

SOURCES = [
    {"id": "catan-base", "filename": "catan_base_rules_2020_200707.pdf", "game": "catan",
     "edition": "base-5", "edition_label": "5th edition · 2020", "document": "CATAN Game Rules & Almanac",
     "pages": [1, 16], "page_count": 16},
    {"id": "catan-seafarers", "filename": "catan-seafarers_2021_rule_book_201201.pdf", "game": "catan",
     "edition": "seafarers-5", "edition_label": "5th edition · 2021", "document": "CATAN Seafarers Game Rules & Scenarios",
     "pages": [1, 32], "page_count": 32},
    {"id": "chess-laws", "filename": "Arbiters_Manual_2025.pdf", "game": "chess",
     "edition": "laws-2023", "edition_label": "2023 Laws · 2025 manual", "document": "FIDE Arbiters’ Manual — Laws of Chess section",
     "pages": [16, 67], "page_count": 355,
     "warning": "This section mixes Laws of Chess and arbiter commentary. Extraction does not yet separate them. Check the original page; do not treat commentary as an official rule."},
    {"id": "dominion-base", "filename": "Dominion2nd.pdf", "game": "dominion",
     "edition": "base-2", "edition_label": "2nd edition · 2021 PDF", "document": "Dominion Base Rules",
     "pages": [1, 16], "page_count": 16},
    {"id": "dominion-dark-ages", "filename": "Dominion-Rules-DarkAges.pdf", "game": "dominion",
     "edition": "dark-ages", "edition_label": "Dark Ages · edition unconfirmed", "document": "Dominion Dark Ages Rules",
     "pages": [1, 12], "page_count": 12, "warning": "The edition of this source still needs confirmation."},
    {"id": "pandemic-base", "filename": "Pandemic_Rulebook.pdf", "game": "pandemic",
     "edition": "base-en", "edition_label": "English base game · edition unconfirmed", "document": "Pandemic Rulebook",
     "pages": [1, 8], "page_count": 8, "warning": "The edition of this source still needs confirmation."},
]

SOURCE_BY_ID = {source["id"]: source for source in SOURCES}
RULESET_SOURCES = {
    ("catan", "base-5"): {"catan-base"},
    ("catan", "seafarers-5"): {"catan-base", "catan-seafarers"},
    ("chess", "laws-2023"): {"chess-laws"},
    ("dominion", "base-2"): {"dominion-base"},
    ("dominion", "dark-ages"): {"dominion-base", "dominion-dark-ages"},
    ("pandemic", "base-en"): {"pandemic-base"},
}


def in_scope(passage, game, edition):
    return passage["game"] == game and passage.get("source_id") in RULESET_SOURCES.get((game, edition), set())
