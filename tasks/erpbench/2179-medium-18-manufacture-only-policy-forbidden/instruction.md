**Priya Shah · Supply & Procurement · Teams**

Each customer order below requires a fulfillment-ready supply solution before its delivery due date:

- Copper Fabricators: 24 units due in 9 days (pretax budget cap $129,968)
- Stonewall Analytics: 17 units due in 10 days (pretax budget cap $96,470)
- Drift Studios West: 19 units due in 11 days (pretax budget cap $107,232)
- Spark Academy: 14 units due in 12 days (pretax budget cap $74,878)
- Helix Workshop: 15 units due in 13 days (pretax budget cap $79,679)
- Ember Dynamics: 17 units due in 13 days (pretax budget cap $94,180)
- Catalyst Guild: 19 units due in 13 days (pretax budget cap $98,949)
- Cedar Cooperative: 19 units due in 14 days (pretax budget cap $101,224)

We have 20 finished units on hand.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.8% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 28.8% portfolio-level new-spend margin at selling price.
* Accounting treats the existing stock as sunk cost.
* Finished-goods purchasing is not allowed right now because our vendors are experiencing a supply chain disruption; rely on in-house manufacturing instead.
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

Work in the `odoo` ERP and commit the plan there.
