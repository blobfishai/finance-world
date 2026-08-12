**Priya Shah · Supply & Procurement · Teams**

Review the open order requests for Coaxial Trunk Harness.

- Bronze Society: 14 units due in 8 days (pretax budget cap $4,558)
- Citadel Dynamics: 18 units due in 8 days (pretax budget cap $8,270)
- Lattice Systems: 23 units due in 8 days (pretax budget cap $9,698)
- Onyx Bazaar: 19 units due in 8 days (pretax budget cap $8,031)
- Arc Reserve: 19 units due in 9 days (pretax budget cap $8,030)
- Northbridge Foundry: 26 units due in 10 days (pretax budget cap $11,609)
- Aether Arena: 14 units due in 11 days (pretax budget cap $5,993)
- Flint Technologies: 19 units due in 14 days (pretax budget cap $8,097)

We have 67 finished units on hand. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.9% at selling price.

## Background & Policy

* The rules for which orders can be accepted are outlined below.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 19 and 22 units.
* Reject or cancel any order that fails those acceptance rules.
* For every order that passes acceptance, provide coverage while spending as little as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.9% new-spend margin at selling price.
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
