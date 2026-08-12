**Priya Shah · Supply & Procurement · Teams**

All orders below for Micro Edge 8U Pod Enclosure need confirmed supply coverage and scheduling.

- Sapphire Research: 1 unit due in 5 days (pretax budget cap $1,656)
- Lumen Labs: 3 units due in 6 days (pretax budget cap $4,694)
- Quartz Boutique: 12 units due in 6 days (pretax budget cap $18,611)
- Ridgeline Partners: 12 units due in 6 days (pretax budget cap $19,049)

Current finished-goods stock is 24 units. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.3% at selling price. After fulfillment, create and post the required linked customer invoices. Use Immediate Payment terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Fulfill all customer orders while respecting all stated policies and constraints.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 24.3% new-spend margin at selling price.
* Available finished stock may be used wherever it helps achieve a constraint-compliant plan.
* After confirming each retained sales order, create and post exactly one linked customer invoice.
* Use Immediate Payment terms on retained sales orders and all linked customer invoices.
* You must create and confirm the necessary sales orders and purchase orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On purchase orders, you must set the delivery date.
* Review Internal Notes/comments on stock, customers, and vendors before you confirm entries in the ERP.

Capacity constraints:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
