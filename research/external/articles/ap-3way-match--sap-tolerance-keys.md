# MM-IV-LIV: Set Tolerance Limits for Incoming Invoice (SAP tolerance keys)

- **URL:** http://teachsap.blogspot.com/2010/02/mm-iv-liv-cre-set-tolerances-for.html
- **Publisher:** teachSAP (reproducing SAP MM Logistics Invoice Verification Customizing documentation)
- **Retrieved:** 2026-08-10
- **Topic:** ap-3way-match

## Summary

The SAP Logistics Invoice Verification (LIV) tolerance-key catalogue. Each key is a two-character code carrying its own lower/upper limits, set per company code; breaching an upper limit generally **blocks the invoice for payment** at posting, requiring a separate release step.

### Tolerance keys (exact codes and published descriptions)

| Key | Description | Limit type | Effect |
|---|---|---|---|
| **AN** | Amount for item without order reference | Absolute upper limit per line item | Blocks item |
| **AP** | Amount for item with order reference | Absolute upper limit per line item | Blocks item |
| **BD** | Form small differences automatically | Absolute (invoice balance) | **Prevents posting** |
| **BR** | Percentage OPUn variance (IR before GR) | Percentage | Blocks for payment |
| **BW** | Percentage OPUn variance (GR before IR) | Percentage | Blocks for payment |
| **DQ** | Exceed amount: quantity variance | Absolute / percentage | Blocks for payment |
| **DW** | Quantity variance when GR quantity = zero | Absolute | Blocks invoice |
| **KW** | Variance from condition value (delivery costs) | Absolute / percentage | Blocks for payment |
| **LA** | Amount of blanket purchase order | Absolute / percentage | Blocks for payment |
| **LD** | Blanket purchase order time limit exceeded | Absolute, in **days** | Blocks for payment |
| **PP** | Price variance | Absolute / percentage | Blocks for payment |
| **PS** | Price variance: estimated price | Absolute / percentage | Blocks for payment |
| **ST** | Date variance (value × days) | Absolute | Blocks for payment |
| **VP** | Moving average price variance | Percentage | Blocks for payment |

### Distinctions worth preserving

- **BD is categorically different**: it defines the window inside which small balance differences are written off automatically; exceeding it **prevents posting** rather than posting-then-blocking. The same is true in spirit for **VP**.
- **DQ vs. DW**: DQ handles quantity variance where a goods receipt exists; **DW covers the case where GR quantity is zero** — i.e. invoice received before any receipt. A zero-GR invoice is a distinct exception, not just a large DQ.
- **BR / BW** are direction-sensitive twins: BR applies when the **invoice receipt precedes the goods receipt**, BW when the **goods receipt precedes the invoice receipt**.
- **ST** is a *value × days* construct — amount multiplied by days of schedule deviation, so a small amount far off schedule and a large amount slightly off schedule can both trip it.
- **LD** is measured in **days** outside the blanket-PO validity period; **LA** caps the cumulative value of a blanket PO.
- **AN vs. AP**: the same absolute per-item amount check, split by whether the item has a **purchase order reference** (AP) or not (AN).
- If a key is **not maintained for a company code, SAP treats it as zero tolerance** and blocks the invoice for any deviation — the opposite of Oracle's blank-means-infinite behaviour.

### Configuration and release

Limits are maintained in Customizing (per company code) — the transaction commonly used is **OMR6**, with lower and upper limits enterable as **absolute** values and as **percentages**. Blocked invoices are released via transaction **MRBR** (Logistics Invoice Verification release), legacy **MR02** for conventional verification, or in background via program **RM08RELEASE**.

## Eval-relevant hooks

- Code-lookup task: map a described variance to the exact key — price difference vs. PO price → **PP**; estimated-price item → **PS**; delivery-cost condition → **KW**; blanket PO past validity → **LD**.
- Zero-GR trap: an invoice posted with no goods receipt should raise **DW**, not DQ.
- Direction test: same quantity variance yields **BR** or **BW** depending on whether IR preceded GR — an agent must ask about sequence before naming the key.
- Cross-ERP contrast assertion: unmaintained SAP tolerance key = zero tolerance (blocks everything); blank Oracle Fusion tolerance = infinite tolerance (blocks nothing). Excellent discriminating question.
- Posting vs. payment block: **BD** breach prevents the invoice from posting at all, whereas **PP/DQ** breaches post the invoice and block it for payment — different remediation paths (fix the invoice vs. release in MRBR).
- Release-path task: name **MRBR** as the release transaction and **RM08RELEASE** for background/mass release.
