**Priya Shah · Supply & Procurement · Teams**

Handle the open Heavy-Duty Specimen Prep Bench order queue.

- Summit Studios South: 16 units due in 8 days (pretax budget cap $34,537)
- Pacific Guild: 15 units due in 9 days (pretax budget cap $22,103)
- Evergreen Council: 26 units due in 11 days (pretax budget cap $59,499)
- Lance Research: 25 units due in 12 days (pretax budget cap $55,957)
- Stonewall Technologies: 16 units due in 12 days (pretax budget cap $35,741)
- Ridgeline Creative: 16 units due in 12 days (pretax budget cap $35,749)
- Sentinel Collective East: 22 units due in 14 days (pretax budget cap $47,429)
- Helix Agency: 24 units due in 14 days (pretax budget cap $54,874)

Current finished-goods stock is 72 units. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.2% at selling price.

## Background & Policy

* These are the rules for customer order acceptance.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 17 and 25 units and allow at least 10 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For every order that passes acceptance, provide coverage while spending as little as possible.
* The combined units covered through new purchasing or manufacturing must clear at least 25.2% portfolio-level new-spend margin at selling price.
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
* Review Internal Notes/comments on stock, customers, and vendors before you confirm entries in the ERP.

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
