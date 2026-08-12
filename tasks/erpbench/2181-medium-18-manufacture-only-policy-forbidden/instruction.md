**Priya Shah · Supply & Procurement · Teams**

Each customer order below requires a fulfillment-ready supply solution before its delivery due date:

- Nexus Enterprises: 14 units due in 8 days (pretax budget cap $76,579)
- Trident Publishing: 17 units due in 8 days (pretax budget cap $92,475)
- Haven Conservatory: 23 units due in 8 days (pretax budget cap $126,470)
- Cardinal Boutique: 21 units due in 8 days (pretax budget cap $113,513)
- Aether Studios South: 15 units due in 11 days (pretax budget cap $78,478)
- Eclipse Archive: 18 units due in 11 days (pretax budget cap $98,638)
- Onyx Cooperative: 21 units due in 11 days (pretax budget cap $116,564)
- Summit Studios East: 16 units due in 11 days (pretax budget cap $90,652)
- Ember Guild: 17 units due in 14 days (pretax budget cap $93,627)

Current finished-goods stock is 22 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.2% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 24.2% portfolio-level new-spend margin at selling price.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
