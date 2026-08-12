**Priya Shah · Supply & Procurement · Teams**

Handle the open Fume Hood Bench Station order queue.

- Stratos Agency: 24 units due in 8 days (pretax budget cap $63,612)
- Silverline Studios South: 20 units due in 9 days (pretax budget cap $57,260)
- Blaze Theater: 14 units due in 11 days (pretax budget cap $32,817)
- Nimbus Reserve: 16 units due in 11 days (pretax budget cap $43,612)
- Cedar Forum: 15 units due in 12 days (pretax budget cap $42,237)
- Haven Trading Co: 20 units due in 13 days (pretax budget cap $54,673)
- Granite Studios North: 26 units due in 13 days (pretax budget cap $71,059)
- Pinnacle Solutions Group: 17 units due in 14 days (pretax budget cap $47,709)

We have 66 finished units on hand. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.4% at selling price.

## Background & Policy

* The rules for which orders can be accepted are outlined below.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 15 and 23 units and allow at least 13 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Once orders are accepted, minimize new procurement or production spend while covering them.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 26.4% new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
* Some sales documents may already exist in draft; review existing documents before creating new ones.
* Cancel any already-drafted sales order that fails those acceptance rules.
* Customer budgets are pre-tax amounts.
* Link every accepted Sales Order to the related Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> PO for every incoming customer order you accept.
* You must sell this product at List Price.
* On every accepted Sales Order, set the commitment date.
* On purchase orders, you must set the delivery date.
* Check Internal Notes/comments on stock, customers, and vendors before you release anything.

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
