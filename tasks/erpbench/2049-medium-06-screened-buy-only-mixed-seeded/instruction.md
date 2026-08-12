**Priya Shah · Supply & Procurement · Teams**

Handle the open Multi-Conductor Trunk Cable order queue.

- Spark Enterprises: 14 units due in 8 days (pretax budget cap $7,442)
- Flux Publishing: 16 units due in 8 days (pretax budget cap $7,939)
- Ember Refinery: 14 units due in 8 days (pretax budget cap $5,228)
- Anvil Council: 26 units due in 8 days (pretax budget cap $13,970)
- Cedar Labs: 16 units due in 9 days (pretax budget cap $8,507)
- Bridgeway Supply Co: 18 units due in 10 days (pretax budget cap $9,576)
- Summit Hub: 24 units due in 12 days (pretax budget cap $12,251)
- Prism Gallery: 19 units due in 12 days (pretax budget cap $9,939)
- Titan Consortium: 14 units due in 12 days (pretax budget cap $6,879)
- Ridgeline Boutique: 19 units due in 13 days (pretax budget cap $10,064)

We have 80 finished units on hand. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.9% at selling price.

## Background & Policy

* Our criteria for accepting incoming customer orders are as follows.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 15 and 25 units.
* Reject or cancel any order that fails those acceptance rules.
* For qualifying orders, ensure fulfillment while keeping new costs down.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 26.9% new-spend margin at selling price.
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
