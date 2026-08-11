# FRP-02 — Basis of preparation for external-company financial summaries

> Contoso Entertainment System USA · Corporate FP&A · effective 2026-01-01 · v2.1
> SIMULATION ONLY

Applies to every summary of a company outside the group that we publish internally: comp
tables in the board pack, counterparty packs, benchmarking exhibits, diligence one-pagers.

## 1. Source of record

The source of record is the **audited consolidated financial statements in Item 8 of the
company's annual report on Form 10-K**, together with the notes to those statements.

Earnings releases (Item 2.02 of Form 8-K and its exhibits), investor decks, transcripts and
company websites are **not** the source of record. They are preliminary and unaudited, they
frequently present measures the company has defined for itself, and they are not comparable
across companies. Where a figure appears in both an earnings release and Item 8, the Item 8
figure governs and the release figure is discarded — including where the release's figure is
labelled GAAP.

Anything labelled *adjusted*, *core*, *underlying*, *pro forma* or *ex-items* is a non-GAAP
measure defined by the company. Never carry one into a comp table, and never use one as the
numerator or denominator of a ratio we compute.

## 2. Net income

**Net income means net income attributable to the registrant** — the line struck after
earnings attributable to noncontrolling interests have been deducted. It is the figure the
registrant's earnings per share is computed on.

The consolidated subtotal presented above that deduction (often labelled simply *Net income*,
and tagged `ProfitLoss` in XBRL) includes earnings the registrant does not own. It is not the
registrant's result and does not go in the comp table.

## 3. Line items and margins

Capture the face of the statement of operations: total revenue, cost of revenue, gross profit,
operating income, net income. Where the statement presents a subtotal, take the subtotal as
presented rather than re-deriving it.

Margins are computed on **total revenue as presented on the face of the statement**, from the
GAAP line items in section 3 — never from a company-defined adjusted measure.

## 4. Year-over-year comparisons

Growth rates are computed **on the basis presented in the most recent filing**, using that
filing's own comparative column for the prior year.

Where a company has recast prior periods — discontinued operations, a segment change, adoption
of a new standard — the recast comparative *is* the prior-year figure. A prior-year amount
lifted from the superseded filing is measured on a different basis, and a growth rate that
splices the two is not a growth rate. Read the basis-of-presentation and discontinued-operations
notes before computing any growth line.

## 5. Units

Amounts are captured in **absolute US dollars**, whatever scale the face of the statement is
presented in. Percentages are captured in percent, to two decimal places.

## 6. Citation

Every summary names the form the figures were taken from. A summary whose figures cannot be
traced to a named filing is not review-ready and is sent back.
