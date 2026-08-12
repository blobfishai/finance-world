**Priya Shah · Supply & Procurement · Teams**

Handle the list of live Cleanroom Preparation Bench order demands.

- Velocity Lyceum: 15 units due in 8 days (pretax budget cap $29,580)
- Nexus Engineering: 26 units due in 9 days (pretax budget cap $66,021)
- Sentinel Workspaces: 19 units due in 9 days (pretax budget cap $44,523)
- Vantage Academy: 22 units due in 9 days (pretax budget cap $51,495)
- Arbor Manufactory: 18 units due in 9 days (pretax budget cap $44,665)
- Cosmo Supply Co: 20 units due in 10 days (pretax budget cap $48,964)
- Cascade Holdings: 17 units due in 11 days (pretax budget cap $40,392)
- Aegis Greenhouse: 26 units due in 11 days (pretax budget cap $65,560)
- Scion Practice: 26 units due in 12 days (pretax budget cap $64,582)

Current finished-goods stock is 74 units. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.2% at selling price.

## Background & Policy

* Order acceptance must follow these rules.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 19 and 25 units and allow at least 9 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For every order that passes acceptance, provide coverage while spending as little as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.2% new-spend margin at selling price.
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
