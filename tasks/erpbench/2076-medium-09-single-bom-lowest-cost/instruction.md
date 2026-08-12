**Priya Shah · Supply & Procurement · Teams**

The following Labeling Applicator System customer orders are firm and must be supplied on schedule:

- Ashford Systems: 14 units due in 8 days (pretax budget cap $147,424)
- Comet Studios East: 25 units due in 9 days (pretax budget cap $270,596)
- Granite Consortium: 16 units due in 9 days (pretax budget cap $179,882)
- Anvil Ventures: 14 units due in 9 days (pretax budget cap $146,518)
- Pinnacle Institute: 20 units due in 12 days (pretax budget cap $213,045)
- Mosaic Chambers: 26 units due in 12 days (pretax budget cap $279,875)
- Cobalt Robotics: 17 units due in 13 days (pretax budget cap $190,692)
- Bayshore Council: 26 units due in 13 days (pretax budget cap $288,440)
- Summit Studios North: 22 units due in 14 days (pretax budget cap $233,368)

On-hand finished stock covers 74 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.9% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 27.9% portfolio-level new-spend margin at selling price.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
