**Dev Bhatt · Payroll & Expense Lead · Teams 09:20**

Morning — I need the February expense file signed off before the 5 March payroll cut-off and
I'd rather you did it than me.

People Ops dropped the extract on the shared drive. Everything on it looks clean: receipts are
attached, nothing's over a cap, nobody flew business. So the per-line check tells me nothing,
and I don't trust the per diem figures at all — those are whatever the traveller typed into the
form, and we reprice them ourselves now under FIN-POL-022.

The other thing I got burned on in Q4: external audit picked up a reimbursement we paid out
tax-free that shouldn't have been, and it cost me a W-2c. So before you send me a number, look
at the dates and not just the amounts.

---

Reply with `submit_answer`:

- `perdiem_due` (number) — USD, total M&IE per diem actually due across the February trips
  once repriced
- `conference_mie_rate` (number) — the full daily M&IE rate you applied to the summit trip
- `nonaccountable_amount` (number) — USD I have to run through payroll as taxable wages
  instead of reimbursing tax-free (0 if there is none)
- `reimbursable_total` (number) — USD of accountable-plan reimbursement for AP to pay out
- `structural_exception_line` (text) — the line that passes every per-line limit and still
  can't be paid the normal way
- `structural_exception_reason` (text) — one sentence on why
