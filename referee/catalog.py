"""Rulebook search choices. This catalogue does not imply AI is connected."""

GAMES = [
    {"id": "catan", "name": "Catan", "editions": [
        {"id": "base-5", "name": "Base game · 5th edition (2020)"},
        {"id": "seafarers-5", "name": "Seafarers · 5th edition (2021)"}],
     "sample": "Can I build a settlement next to another settlement?"},
    {"id": "chess", "name": "Chess", "editions": [
        {"id": "laws-2023", "name": "2023 Laws · 2025 Arbiters’ Manual"}],
     "sample": "Can I castle while my king is in check?"},
    {"id": "dominion", "name": "Dominion", "editions": [
        {"id": "base-2", "name": "Base game · 2nd edition"},
        {"id": "dark-ages", "name": "Dark Ages · edition to verify"}],
     "sample": "How many cards do I draw at the end of my turn?"},
    {"id": "pandemic", "name": "Pandemic", "editions": [
        {"id": "base-en", "name": "English base game · edition to verify"}],
     "sample": "What happens when an outbreak occurs?"},
]
