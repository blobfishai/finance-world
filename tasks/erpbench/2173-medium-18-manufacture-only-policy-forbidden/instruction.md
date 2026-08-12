**Priya Shah · Supply & Procurement · Teams**

Plan fulfillment for these outstanding Gowning Room Airlock System orders to ensure timely deliveries:

- Marble Conservatory: 21 units due in 8 days (pretax budget cap $156,761)
- Scion Interactive: 15 units due in 8 days (pretax budget cap $120,548)
- Alpine Atelier: 22 units due in 9 days (pretax budget cap $175,451)
- Terra Hub: 15 units due in 9 days (pretax budget cap $120,806)
- Hartland Cooperative: 14 units due in 10 days (pretax budget cap $108,607)
- Thornton Academy: 18 units due in 10 days (pretax budget cap $141,052)
- Clearwater Works: 17 units due in 11 days (pretax budget cap $133,127)
- Indigo Advisory: 14 units due in 11 days (pretax budget cap $109,078)
- Trellis Architects: 16 units due in 12 days (pretax budget cap $123,099)
- Cascade Consortium: 18 units due in 13 days (pretax budget cap $138,601)

Current finished-goods stock is 29 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.6% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 25.6% new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
* Finished-goods procurement is not allowed in this planning cycle because finance has frozen budget for direct replenishment; rely on in-house manufacturing instead.
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
