**Priya Shah · Supply & Procurement · Teams**

Prepare a fulfillment strategy for all listed Modular Cleanroom Panel System ISO 7 orders to meet due dates and avoid shortages.

- Bayshore Gallery: 20 units due in 9 days (pretax budget cap $263,509)
- Gateway Trust: 26 units due in 9 days (pretax budget cap $343,586)
- Granite Systems: 19 units due in 9 days (pretax budget cap $242,579)
- Nexus Conservatory: 19 units due in 11 days (pretax budget cap $250,063)
- Pinnacle Fabricators: 22 units due in 11 days (pretax budget cap $281,046)
- Prism Studios: 17 units due in 12 days (pretax budget cap $224,318)
- Garnet Office: 14 units due in 13 days (pretax budget cap $180,726)
- Aether Pavilion: 15 units due in 13 days (pretax budget cap $199,479)
- Matrix Studios East: 19 units due in 14 days (pretax budget cap $242,490)

Current finished-goods stock is 32 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.5% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.5% new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
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
