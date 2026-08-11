**Joel Tan · FP&A Manager · Teams 09:12**

Ardent sent back the register for the 16–28 Feb half and I have to sign it off before the pay
file releases Thursday — and the labour accrual goes in off the same number.

I ran my usual eyeball over it: hours total agrees to the timekeeping export, gross total looks
sane, so on the face of it there's nothing in there. But Comp pushed through the January grade
changes late and I don't fully trust what the bureau has on its master file, and HR had at
least one leave block in the period. Can you do the proper tie-out per SOP-PAY-04 rather than
my eyeball version?

Two things I care about: I don't want to fund a correction for something that isn't actually
wrong, and if anyone was short-paid I need the name today so it goes on the off-cycle run.

---

Reply with `submit_answer`:

- `discrepancy_employee_ids` (text) — employee IDs of the lines that are genuinely wrong
- `overpayment_usd` (number) — total gross overpaid across those lines
- `underpayment_usd` (number) — total gross underpaid across those lines, as a positive number
- `net_variance_usd` (number) — signed net for the accrual: gross paid minus gross owed, so a
  net overpayment is positive and a net underpayment is negative
- `underpaid_employee` (text) — the employee ID and name of whoever was short-paid
