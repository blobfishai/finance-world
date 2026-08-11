You are the controller closing February for legal entity **CESP** (CES Programs LLC).
Today is March 2, 2026.

The close checklist is in the docs library and the reconciliation workbook is on the
shared drive. Tie the AR and AP subledger balances in the ERP to the workbook figures and
identify the line that does not agree.

Submit via harness `submit_answer`:

- `erp_ar_balance` (number, USD — CESP open AR per the ERP)
- `erp_ap_balance` (number, USD — CESP open AP per the ERP)
- `unreconciled_subledger` (string — "AR" or "AP", whichever fails to tie)
- `variance_amount` (number, USD — absolute difference on that line)
- `blocking_task_owner` (string — who owns the failing checklist task)
