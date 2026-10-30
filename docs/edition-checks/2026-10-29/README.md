# Pandemic and Dark Ages source and edition check

Checked on 29 October 2026 (Hong Kong). Prepared with AI assistance for Lu
Weidi's source-verification task. Independent team review remains pending.

## Conclusion

The source check and findings record due 1 November are complete. Both local
PDFs match the existing pinned manifest. Pandemic also matches a freshly
retrieved official download byte for byte. The Dark Ages official PDF was
readable through the web research reader, but a separate direct download
returned HTTP 403, so its current online byte identity was not established.
Neither inspected rulebook establishes an explicit numbered edition or exact
physical printing. Retain the existing uncertainty labels pending team review.
Copyright years, file timestamps and URL folders are separate evidence, not
interchangeable edition identifiers. No application metadata, PDF or index was
changed by this check.

## Evidence by source

| Item | Pandemic | Dominion Dark Ages |
| --- | --- | --- |
| Local filename | `rulebooks/Pandemic_Rulebook.pdf` | `rulebooks/Dominion-Rules-DarkAges.pdf` |
| PDF pages | 8 | 12 |
| Official product page | [Z-Man Games](https://www.zmangames.com/game/pandemic/) | [Rio Grande Games](https://www.riograndegames.com/games/dominion-dark-ages/) |
| Official PDF | [English base-game rulebook](https://cdn.svc.asmodee.net/production-zman/uploads/2024/09/Pandemic_Rulebook.pdf) | [Dark Ages rulebook](https://www.riograndegames.com/wp-content/uploads/2022/03/Dominion-Rules-DarkAges.pdf) |
| Local file versus pinned manifest | SHA-256 matches | SHA-256 matches |
| Fresh direct PDF download | HTTP 200; 6,218,245 bytes; SHA-256 matches local file and manifest | HTTP 403; no fresh binary hash comparison available |
| Edition/printing decision | Official English base-game source verified; exact edition/printing not explicitly identified | Official-hosted expansion PDF inspected; numbered edition/printing not explicitly identified; fresh binary identity unverified |

### Pandemic observations

The publisher's product page links its **Pandemic Rulebook English** download
to the exact URL in the project manifest. The page's base-game component list
is consistent with the local PDF's opening page. PDF page 8 visibly carries a
2013 Z-Man Games copyright notice; it was checked in both extracted text and a
rendered image. PDF metadata records creation on 6 November 2019 and modification
on 12 December 2019. The URL has a 2024/09 upload folder. None of these dates is
an explicit edition/printing declaration. The fresh remote SHA-256 matches the
local pinned file. It is supported to identify this as the publisher-linked
English base-game PDF, but not to relabel it as a 2024 edition or a specific
printing. A numbered edition was not established for these exact bytes.

### Dark Ages observations

The local cover describes the seventh Dominion expansion; this is an expansion
sequence number, not an edition number. The local PDF's page 12 visibly carries
copyright years 2012, 2017 and 2020. Its layout header identifies
`DomDarkAgesRules2020.qxp_WideDominion` with a 5 February 2020 timestamp. Metadata
records creation in 2020 and modification on 10 March 2022; the URL contains
2022/03. These observations support the document's production history, not a
formal "2020 edition" or "2022 edition." The web reader opened the official
12-page PDF and showed the same copyright years. Direct product-page requests
and the independent binary-download attempt returned HTTP 403. Consequently,
current product-page-to-PDF linking and remote binary equality are not claimed.

## Local document fingerprints

- Pandemic: `f1d93b126f13d53decea29ef04a8cb549687b36de5ab0b479567216f2d8a8a61`
- Dark Ages: `c8b770b5b80daafa08e12d7f91076ab64acebc97b3779d3c7899bbfabee53fdc`

The raw metadata, inspected page references and download-comparison outcomes
are recorded in [evidence.json](evidence.json). PDF page numbers above are
one-based. Browser screenshots/renders were used for inspection only; full
copyrighted rulebooks have not been added to Git.

## Handoff for the 8 November milestone

1. A teammate checks the linked sources and local copyright pages. If possible,
   open the Dark Ages publisher page/download in a normal browser and compare
   the downloaded file's SHA-256 with the fingerprint above. Record the outcome;
   a failed automated request does not establish that the source is unavailable
   to all users.
2. Review metadata wording in `referee/sources.py` and
   `docs/rulebook-sources.json`. Distinguish verified provenance from unresolved
   edition/printing. Preserve the current ruleset IDs, PDFs, pinned hashes and
   page ranges unless a separately reviewed source change is approved.
3. Record the team's reviewer/date and any metadata changes in a reviewable
   commit by 8 November. If numbered editions remain unconfirmed, retain an
   explicit uncertainty label. Rebuild/retest only if source content or answering
   behavior changes. This check does not grant external-model or redistribution
   permissions, which remain separate from source provenance.
