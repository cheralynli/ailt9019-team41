"""Rebuild ignored local search data: python -m referee.indexer.

Pages remain citation boundaries. Text is normalized, not paraphrased.
"""

import hashlib
import json
from pathlib import Path
import re
import unicodedata

from .sources import SOURCES

ROOT = Path(__file__).resolve().parents[1]


def normalize(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def chunks(text, size=500, overlap=80):
    words = text.split()
    for start in range(0, len(words), size - overlap):
        yield " ".join(words[start:start + size])
        if start + size >= len(words):
            break


def build_index(root=ROOT):
    from pypdf import PdfReader

    passages, reports = [], []
    # Read all sources before replacing output; missing/changed documents fail closed.
    for source in SOURCES:
        path = root / "rulebooks" / source["filename"]
        reader = PdfReader(path)
        if len(reader.pages) != source["page_count"]:
            raise ValueError(f"Unexpected page count for {source['filename']}; verify this edition before indexing.")
        if source["id"] == "chess-laws":
            from .chess import extract_chess, PROFILE
            separated, audit = extract_chess(path)
            passages.extend(separated)
            reports.append({"source_id": source["id"], "filename": source["filename"],
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "pdf_pages": len(reader.pages), "indexed_range": source["pages"],
                            "passages": len(separated), "skipped_short_pages": [],
                            "extraction_profile": PROFILE, "page_classification": audit})
            continue
        start, end = source["pages"]
        empty_pages = []
        before = len(passages)
        for page_number in range(start, end + 1):
            text = normalize(reader.pages[page_number - 1].extract_text() or "")
            if len(text) < 30:
                empty_pages.append(page_number)
                continue
            for index, chunk in enumerate(chunks(text)):
                passages.append({
                    "id": f"{source['id']}-p{page_number}-{index + 1}",
                    "source_id": source["id"], "game": source["game"],
                    "edition": source["edition"], "edition_label": source["edition_label"],
                    "document": source["document"], "page": page_number,
                    "printed_page": str(page_number - 9) if source["game"] == "chess" else None,
                    "kind": "rules_and_commentary_unseparated" if source["game"] == "chess" else "rulebook_excerpt",
                    "warning": source.get("warning", ""), "text": chunk,
                })
        reports.append({"source_id": source["id"], "filename": source["filename"],
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "pdf_pages": len(reader.pages), "indexed_range": [start, end],
                        "passages": len(passages) - before, "skipped_short_pages": empty_pages})
    if any(report["passages"] == 0 for report in reports):
        raise ValueError("A source produced no searchable text; inspect it before proceeding.")
    report = {"sources": reports, "passage_count": len(passages),
              "excluded_files": sorted(p.name for p in (root / "rulebooks").glob("*.pdf")
                                       if p.name not in {s["filename"] for s in SOURCES})}
    data = root / "data"
    data.mkdir(exist_ok=True)
    temporary = data / "passages.json.tmp"
    temporary.write_text(json.dumps(passages, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(data / "passages.json")
    (data / "index-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    try:
        print(json.dumps(build_index(), indent=2))
    except (OSError, ValueError, ImportError) as error:
        raise SystemExit(f"Index build failed: {error}")
