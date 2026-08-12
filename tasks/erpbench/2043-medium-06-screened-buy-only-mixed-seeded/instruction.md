**Priya Shah · Supply & Procurement · Teams**

Handle the list of live Control Signal Cable Assembly order demands.

- Scion Gallery: 24 units due in 8 days (pretax budget cap $7,682)
- Granite Analytics: 23 units due in 9 days (pretax budget cap $6,938)
- Onyx Trust: 19 units due in 9 days (pretax budget cap $6,126)
- Ridgeline Productions: 17 units due in 10 days (pretax budget cap $5,444)
- Mosaic Publishing: 15 units due in 10 days (pretax budget cap $3,249)
- Solace Clinics: 16 units due in 11 days (pretax budget cap $4,716)
- Polar Practice: 26 units due in 11 days (pretax budget cap $8,034)
- Crown Workshop: 23 units due in 11 days (pretax budget cap $7,335)
- Nimbus Conservatory: 26 units due in 14 days (pretax budget cap $8,183)

Current finished-goods stock is 87 units. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.3% at selling price.

## Background & Policy

* These are the rules for customer order acceptance.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 24 and 25 units.
* Reject or cancel any order that fails those acceptance rules.
* For every accepted order, fulfill it while keeping additional procurement or manufacturing outflow to a minimum.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.3% at selling price.
* Finance considers the existing stock as sunk cost.
* Some sales documents may already exist in draft; review existing documents before creating new ones.
* Cancel any already-drafted sales order that fails those acceptance rules.
* Customer budgets are pre-tax amounts.
* Link every accepted Sales Order to the related Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> PO for every incoming customer order you accept.
* You must sell this product at List Price.
* On every accepted Sales Order, set the commitment date.
* On purchase orders, you must set the delivery date.
* Before releasing anything, read the Internal Notes/comments on stock, customers, and vendors.

Fulfillment constraints for accepted orders:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
