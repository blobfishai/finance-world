**Priya Shah · Supply & Procurement · Teams**

All orders below for Architectural Pendant Luminaire need confirmed supply coverage and scheduling.

- Westfield Outfitters: 14 units due in 10 days (pretax budget cap $10,180)
- Ironwood Supply Co: 26 units due in 10 days (pretax budget cap $19,396)
- Mosaic Enterprises: 22 units due in 11 days (pretax budget cap $15,472)
- Quartz Bazaar: 19 units due in 12 days (pretax budget cap $13,565)
- Hartland Works: 23 units due in 12 days (pretax budget cap $17,691)
- Granite Fabricators: 21 units due in 12 days (pretax budget cap $16,091)
- Jade Hub: 17 units due in 12 days (pretax budget cap $12,281)
- Cascade Institute: 26 units due in 13 days (pretax budget cap $19,792)

Current finished-goods stock is 76 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.5% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.5% at selling price.
* Accounting treats the existing stock as sunk cost.
* You must create and confirm the necessary sales orders, purchase orders, and/or manufacturing orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> PO or SO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* If you choose to manufacture, you must procure the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
