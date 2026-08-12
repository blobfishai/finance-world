**Priya Shah · Supply & Procurement · Teams**

Ensure all these Refrigerated Dock Leveler Package customer orders are supplied on schedule:

- Aurora Studios North: 22 units due in 8 days (pretax budget cap $230,558)
- Hartland Partners: 26 units due in 8 days (pretax budget cap $284,044)
- Ironside Cooperative: 18 units due in 9 days (pretax budget cap $187,780)
- Northbridge Advisory: 16 units due in 10 days (pretax budget cap $172,356)
- Noble Manufactory: 21 units due in 11 days (pretax budget cap $222,923)
- Ridge Agency: 26 units due in 12 days (pretax budget cap $295,316)
- Velocity Studios West: 26 units due in 12 days (pretax budget cap $271,839)
- Nimbus Sciences: 26 units due in 13 days (pretax budget cap $284,437)
- Brookfield Innovations: 26 units due in 14 days (pretax budget cap $289,501)

We have 38 finished units on hand.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29% new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
* You must create and confirm the necessary sales orders, manufacturing orders, and any component purchase orders needed for assembly.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* Use in-house manufacturing to cover finished-goods shortfalls; purchase orders are only for components.
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* Procure only the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Review Internal Notes/comments on stock, customers, vendors, and workcenters before you confirm entries in the ERP.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
