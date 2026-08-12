**Priya Shah · Supply & Procurement · Teams**

Plan fulfillment for these outstanding Biosafety Cabinet Class II Type A2 orders to ensure timely deliveries:

- Pinnacle Pavilion: 23 units due in 8 days (pretax budget cap $246,666)
- Spark Greenhouse: 14 units due in 8 days (pretax budget cap $146,614)
- Cascade Clinics: 20 units due in 9 days (pretax budget cap $221,736)
- Marble Academy: 16 units due in 10 days (pretax budget cap $167,455)
- Fairview Pictures: 20 units due in 10 days (pretax budget cap $222,901)
- Alloy Designs: 15 units due in 11 days (pretax budget cap $163,774)
- Ridgeline Atelier: 26 units due in 11 days (pretax budget cap $293,607)
- Raven Brands: 26 units due in 12 days (pretax budget cap $272,473)

We have 30 finished units on hand.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.5% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.5% new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

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
