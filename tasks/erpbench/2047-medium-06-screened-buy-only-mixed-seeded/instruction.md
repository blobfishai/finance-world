**Priya Shah · Supply & Procurement · Teams**

Handle the list of live Sensor Cable Harness order demands.

- Nexus Studios North: 14 units due in 8 days (pretax budget cap $2,599)
- Trellis Architects: 26 units due in 9 days (pretax budget cap $6,485)
- Slate Studios East: 14 units due in 11 days (pretax budget cap $3,516)
- Westfield Brands: 19 units due in 11 days (pretax budget cap $4,901)
- Helix Institute: 14 units due in 12 days (pretax budget cap $3,501)
- Osprey Pictures: 23 units due in 12 days (pretax budget cap $6,012)
- Quantum Bureau: 25 units due in 14 days (pretax budget cap $6,186)
- Pivot Studios South: 18 units due in 14 days (pretax budget cap $4,616)
- Keystone Media: 18 units due in 14 days (pretax budget cap $4,415)

We have 74 finished units on hand. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.4% at selling price.

## Background & Policy

* The rules for which orders can be accepted are outlined below.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 15 and 22 units.
* Reject or cancel any order that fails those acceptance rules.
* For every accepted order, provide supply coverage with minimal new spend.
* The combined units covered through new purchasing or manufacturing must clear at least 27.4% portfolio-level new-spend margin at selling price.
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
