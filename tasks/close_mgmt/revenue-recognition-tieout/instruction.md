**Iris Bhatt · Revenue Accounting Manager · Teams 07:50**

The auditors moved the revenue walkthrough to Thursday and the FY26 contract register goes out
with the PBC pack. Can you tie it out to the recognition schedule per RAP-04 before I send it?

Last year we handed them a register that footed perfectly and still took two cut-off findings.
Nobody caught them in-house, because the totals agreed. So please don't only foot it.

Also — don't lean on the recognised column in the register. Someone refreshes that by hand and
I have no idea when it was last done.

Over- and under-recognised go on separate lines. Netting them is how a real exposure turns into
a rounding difference on the memo, and the auditors ask for the directions anyway.

---

Reply with `submit_answer`:

- `flagged_contracts` (text) — every contract ID with a recognition exception, comma-separated
- `amount_exceptions` (text) — the contract IDs whose recognised total does not tie
- `timing_exceptions` (text) — the contract IDs whose total ties but whose schedule does not
- `over_recognised_usd` (number) — USD recognised in excess of contract value, across the
  amount exceptions
- `under_recognised_usd` (number) — USD short of contract value, across the amount exceptions
