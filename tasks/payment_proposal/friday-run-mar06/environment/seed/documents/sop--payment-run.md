# Payment Run SOP (AP-SOP-002)

> SIMULATION ONLY

**Owner:** AP Manager · **Version:** 1.0 · **Effective:** 2026-01-01

Weekly payment run, executed Fridays. The proposal is assembled by Monday EOD and posted
by a human approver Thursday.

Selection rules for a run with payment date **P**:
1. Include every open vendor invoice with due date on or before **P + 3 days** (avoids
   weekend lates).
2. Include every open invoice whose cash-discount window is still open on **P** —
   discounts at 2/10-net-30 economics (~36% annualized) are always taken
   (see AP-POL-007, Cash Discount Capture).
3. **Exclude all invoices of vendors on payment hold** — no exceptions; note them for the
   AP manager instead.
4. Discount value = discount % × open amount, taken at settlement; net cash out =
   gross included amount − discounts captured.
