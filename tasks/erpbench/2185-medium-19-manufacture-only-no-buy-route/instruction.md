**Priya Shah · Supply & Procurement · Teams**

Supply plans must be created to fulfill each outstanding Rail Dock Leveler Board 40000lb customer order listed.

- Mosaic Advisory: 15 units due in 8 days (pretax budget cap $169,757)
- Onyx Institute: 21 units due in 8 days (pretax budget cap $222,449)
- Ironwood Manufactory: 26 units due in 8 days (pretax budget cap $295,825)
- Summit Workshop: 14 units due in 8 days (pretax budget cap $155,567)
- Eclipse Refinery: 19 units due in 9 days (pretax budget cap $201,073)
- Polar Supply Co: 17 units due in 9 days (pretax budget cap $183,658)
- Copper Media: 18 units due in 12 days (pretax budget cap $189,293)
- Ivory Initiative: 15 units due in 12 days (pretax budget cap $162,120)
- Cobalt Partners: 26 units due in 13 days (pretax budget cap $279,056)

We have 34 finished units on hand.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.1% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 25.1% portfolio-level new-spend margin at selling price.
* Accounting treats the existing stock as sunk cost.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
