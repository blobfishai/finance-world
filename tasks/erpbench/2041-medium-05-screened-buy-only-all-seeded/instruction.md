**Priya Shah · Supply & Procurement · Teams**

Handle the list of live Wet Lab Sink Bench order demands.

- Riverdale Ventures: 14 units due in 8 days (pretax budget cap $29,686)
- Cascade Studios East: 14 units due in 8 days (pretax budget cap $20,466)
- Alpine Alliance: 17 units due in 9 days (pretax budget cap $33,688)
- Ironwood Solutions Group: 19 units due in 10 days (pretax budget cap $37,734)
- Crestview Fabricators: 16 units due in 10 days (pretax budget cap $31,927)
- Lattice Reserve: 17 units due in 10 days (pretax budget cap $33,442)
- Lakewood Collective East: 14 units due in 10 days (pretax budget cap $29,164)
- Equinox Agency: 15 units due in 10 days (pretax budget cap $31,012)
- Aether Group: 17 units due in 11 days (pretax budget cap $34,083)
- Stratos Labs: 17 units due in 12 days (pretax budget cap $34,463)

We have 68 finished units on hand. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.7% at selling price.

## Background & Policy

* Customer order acceptance will be determined as follows.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 15 and 16 units and allow at least 9 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Once orders are accepted, minimize new procurement or production spend while covering them.
* The combined units covered through new purchasing or manufacturing must clear at least 29.7% portfolio-level new-spend margin at selling price.
* Accounting treats the existing stock as sunk cost.
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
