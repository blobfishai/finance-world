**Priya Shah · Supply & Procurement · Teams**

Prepare a fulfillment strategy for all listed Mechanical Dock Leveler 30000lb orders to meet due dates and avoid shortages.

- Ivory Trust: 24 units due in 8 days (pretax budget cap $116,141)
- Mosaic Studios West: 17 units due in 8 days (pretax budget cap $81,210)
- Zenith Conservatory: 18 units due in 9 days (pretax budget cap $86,683)
- Aegis Designs: 14 units due in 9 days (pretax budget cap $63,354)
- Equinox Works: 15 units due in 9 days (pretax budget cap $70,203)
- Lance Theater: 21 units due in 9 days (pretax budget cap $94,941)
- Ironwood Architects: 16 units due in 11 days (pretax budget cap $71,981)
- Globe Studios East: 23 units due in 11 days (pretax budget cap $106,910)
- Flint Supply Co: 14 units due in 12 days (pretax budget cap $68,345)

Current finished-goods stock is 24 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28% at selling price.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
