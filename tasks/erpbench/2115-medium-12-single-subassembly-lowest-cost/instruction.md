**Priya Shah · Supply & Procurement · Teams**

Each customer order below requires a fulfillment-ready supply solution before its delivery due date:

- Riverdale Academy: 26 units due in 8 days (pretax budget cap $1,433,641)
- Bridgeway Research: 26 units due in 9 days (pretax budget cap $1,349,618)
- Skyline Theater: 24 units due in 10 days (pretax budget cap $1,216,243)
- Catalyst Advisory: 20 units due in 10 days (pretax budget cap $1,066,134)
- Osprey Partners: 21 units due in 10 days (pretax budget cap $1,060,339)
- Titan Supply Co: 14 units due in 10 days (pretax budget cap $759,414)
- Oakmont Outfitters: 17 units due in 11 days (pretax budget cap $936,757)
- Crown Greenhouse: 20 units due in 11 days (pretax budget cap $1,047,974)
- Arbor Institute: 26 units due in 14 days (pretax budget cap $1,308,573)
- Apex Cooperative: 26 units due in 14 days (pretax budget cap $1,331,748)

We have 115 finished units on hand. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.1% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.1% new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
* You must create and confirm the necessary sales orders, purchase orders, and/or manufacturing orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* For subassembly or intermediate MOs, put the immediate parent MO reference(s) that the subassembly feeds (e.g. WH/MO/00020 or WH/MO/00020, WH/MO/00021) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> (Subassembly MO if needed) -> PO or SO -> PO.
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
