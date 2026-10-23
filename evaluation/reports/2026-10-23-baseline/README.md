# Live baseline review — 23 October 2026

Run: `20261023T074834320188Z`, `qwen3.8-flash`, commit
`7ab82d43cbc80f3d97cc584644b6396d2cfdd39a`. All 32 cases completed with no API
errors. The frozen suite and original timestamped results were preserved.

This is an **assistant-assisted, conservative evidence review**, not independent
human adjudication. Team confirmation is pending, especially for added wording
and scope ambiguities. The CSV records generated answers, compact source
references, individual decisions and reasons; it omits full copyrighted excerpts
and credentials. The summary records the raw-output hash for provenance.

| Measure | Baseline | Required |
| --- | --- | --- |
| Correct full rulings | 22/26 | 21/26 |
| Sufficient actual citations | 21/26 | 24/26 |
| Appropriate refusals | 6/6 | 6/6 |

Overall: **not passed**. All six answerable Chess cases correctly use verified
formal-law passages, and both Chess refusal cases behave appropriately. These
results concern the fixed cases only, not all possible Chess questions.

## Failures requiring retest

- **CAT02:** Correct settlement cost, but additional mandatory after-trading timing
  is unsupported by the actual cited excerpt. Conservatively fail the full answer
  as well as citation sufficiency; the core cost alone is correct.
- **CAT05:** The new-island answer correctly mentions the distance rule. Its actual
  Seafarers citations name that rule without stating the adjacent-intersection
  restriction explained in the answer. Include the base rule itself when stating
  those conditions; otherwise decline to supply unsupported details.
- **CAT06:** Answerable ship-cost/movement question was refused because search
  omitted the cost passage. Correct costs are one wool and one lumber, with no
  movement on the construction turn.
- **PAN01:** “Exactly 4” overstates an allowance of up to four actions. The question
  and source require preserving the optional limit.
- **PAN05:** Winning on all four cures is correct. The final sentence wrongly
  widens the eradication restriction to all cubes in cities of that color;
  eradication prevents cubes of the eradicated disease color, not other colors.

Alternative valid citations were accepted for DOM02, DOM04, DOM05 and DOM06.
The 19/26 designated-anchor preflight result was not used as an accuracy score.
Two-part questions require both facts to be supported, not exactly two citations
when one source location explicitly supplies both facts (DOM05).

## Changes after this baseline

Search now reserves evidence for explicit subquestions, carries an unambiguous
object into a follow-up search clause, and recognizes nearby cost/payment
language. Expansion settlement searches also include the base distance-rule
definition when an excerpt references it. The ship regression checks both necessary passages and
ruleset isolation. The prompt requires supporting every claim with the actual
cited excerpts, omitting unrelated mechanics, and preserving maxima and disease
color scope. These are development fixes, not evidence that the new live run
passes. The answer key has not been changed to match model outputs.

All 47 automated tests pass without live model requests. The post-fix offline
preflight covers 21/26 designated reference sets; alternate valid citations still
require semantic review.

Run `zsh scripts/start-course.zsh --evaluate` again, entering the key locally.
Review all 32 new outputs, including previously passing cases; sequential calls
use the shared group quota. Record the new run separately and score its completed
review. Prompt instructions and lexical search cannot guarantee semantic accuracy.
