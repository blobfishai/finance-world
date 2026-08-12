**Priya Shah · Supply & Procurement · Teams**

Ensure all these Laser Safety Curtain System customer orders are supplied on schedule:

- Pacific Productions: 26 units due in 8 days (pretax budget cap $80,047)
- Ashford Reserve: 14 units due in 8 days (pretax budget cap $42,618)
- Catalyst Solutions Group: 14 units due in 9 days (pretax budget cap $43,199)
- Baltic Creative: 18 units due in 10 days (pretax budget cap $53,637)
- Sapphire Society: 22 units due in 10 days (pretax budget cap $70,041)
- Pivot Engineering: 26 units due in 10 days (pretax budget cap $79,823)
- Northbridge Consortium: 26 units due in 11 days (pretax budget cap $83,344)
- Horizon Studios East: 26 units due in 11 days (pretax budget cap $79,060)
- Bronze Workspaces: 26 units due in 14 days (pretax budget cap $80,473)

Current finished-goods stock is 82 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.8% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 25.8% new-spend margin at selling price.
* Use the finished stock on hand where it helps reduce demand on shared workcenters.
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
