**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Softwall Curtain Cleanroom ISO 8 require confirmed supply to proceed with fulfillment:

- Polar Pavilion: 15 units due in 8 days (pretax budget cap $108,880)
- Eclipse Enterprises: 22 units due in 8 days (pretax budget cap $170,359)
- Raven Designs: 14 units due in 9 days (pretax budget cap $101,990)
- Beacon Labs: 15 units due in 10 days (pretax budget cap $112,997)
- Meridian Practice: 16 units due in 10 days (pretax budget cap $117,528)
- Comet Agency: 14 units due in 11 days (pretax budget cap $104,621)
- Sierra Sciences: 18 units due in 12 days (pretax budget cap $141,399)
- Westfield Supply Co: 14 units due in 12 days (pretax budget cap $108,507)
- Ridge Boutique: 14 units due in 14 days (pretax budget cap $101,246)
- Stonewall Brands: 18 units due in 14 days (pretax budget cap $142,573)

Current finished-goods stock is 26 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.7% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 26.7% portfolio-level new-spend margin at selling price.
* Accounting treats the existing stock as sunk cost.
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
