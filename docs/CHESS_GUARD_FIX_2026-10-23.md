# Chess source-policy fix — 23 October 2026

## Problem

The previous pipeline blocked model answers only when a retrieved passage had
`kind=rules_and_commentary_unseparated`. The corpus loader allowed that optional
field to be missing or incorrect. Such an index could therefore enable Chess
model calls even though the source still mixed official laws and commentary.

## Change

The approved Chess source now explicitly disallows AI answers in the checked-in
source policy. The pipeline checks this trusted policy instead of the index's
classification field. The loader also canonicalizes classification metadata from
that policy. Existing indexes need no rebuild to receive this protection.

This preserves Chess source search and citations; it does not separate commentary
or claim completion of Chess AI integration. Other permitted sources continue to
reach the model adapter.

## Verification

33 automated tests passed with the six local PDFs and generated index present.
New regression coverage checks missing, misleading and normal classification
metadata through both direct pipeline calls and the corpus loader. It asserts
that the model is never called for the restricted source and confirms that an
allowed Catan source still reaches the model adapter.

All provider requests in tests are mocked. No real API key or course credits
were used. The existing full rules-evaluation and deployment gaps remain.
