**Priya Shah · Supply & Procurement · Teams**

Ensure all these Open-Plan Noise Barrier Wall customer orders are supplied on schedule:

- Echo Theater: 5 units due in 5 days (pretax budget cap $3,656)
- Lakewood Engineering: 11 units due in 6 days (pretax budget cap $7,986)
- Raven Creative: 12 units due in 7 days (pretax budget cap $8,448)
- Mosaic Lyceum: 12 units due in 9 days (pretax budget cap $8,723)

Current finished-goods stock is 34 units. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.1% at selling price.

## Background & Policy

* Get every customer order covered without violating any stated policy or constraint.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.1% at selling price.
* Finished stock is available and may be used where it helps satisfy the stated constraints.
* You must create and confirm the necessary sales orders and purchase orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On purchase orders, you must set the delivery date.
* Check Internal Notes/comments on stock, customers, and vendors before you release anything.

Capacity constraints:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
