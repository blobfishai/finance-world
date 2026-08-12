**Priya Shah · Supply & Procurement · Teams**

All orders below for Parking Garage Canopy Light need confirmed supply coverage and scheduling.

- Pivot Museum: 18 units due in 9 days (pretax budget cap $6,837)
- Lumen Architects: 15 units due in 9 days (pretax budget cap $5,683)
- Citadel Designs: 14 units due in 10 days (pretax budget cap $5,223)
- Cedar Publishing: 18 units due in 10 days (pretax budget cap $6,806)
- Atlas Observatory: 18 units due in 10 days (pretax budget cap $6,630)
- Echo Robotics: 17 units due in 10 days (pretax budget cap $6,562)
- Prism Studios West: 17 units due in 11 days (pretax budget cap $6,221)
- Polar Council: 20 units due in 13 days (pretax budget cap $7,624)
- Crest Greenhouse: 15 units due in 13 days (pretax budget cap $5,453)
- Comet Cooperative: 18 units due in 14 days (pretax budget cap $7,019)

Current finished-goods stock is 75 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.6% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 25.6% new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
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
