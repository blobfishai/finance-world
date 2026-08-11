**Ana Duarte · AR Manager · Teams 08:45**

Four short-pays came in this week — CINV-701 through CINV-704. Can you code and route them
per SOP-AR-06 before the AR bridge goes out?

Don't just take the reason off the remittance. We had one last quarter coded as a damages
claim on the customer's say-so and it turned out to be a price they'd never agreed; we
conceded 12k we should have charged back.

Conceded and chargeback go on separate lines of the bridge — don't net them.

---

Reply with `submit_answer`:

- `total_deductions` (number) — USD across all four
- `cinv701_reason` · `cinv702_reason` · `cinv703_reason` · `cinv704_reason` (text) — the
  reason code from the ERP taxonomy for each
- `conceded_amount` (number) — USD to be credited
- `chargeback_amount` (number) — USD to be charged back and pursued
