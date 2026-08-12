**Priya Shah · Supply & Procurement · Teams**

Ensure all these Hydraulic Dock Leveler 25000lb customer orders are supplied on schedule:

- Evergreen Greenhouse: 16 units due in 8 days (pretax budget cap $118,275)
- Cosmo Studios West: 16 units due in 8 days (pretax budget cap $123,472)
- Quartz Outfitters: 22 units due in 9 days (pretax budget cap $168,975)
- Arrow Labs: 26 units due in 10 days (pretax budget cap $203,779)
- Ember Atelier: 26 units due in 13 days (pretax budget cap $193,284)
- Pivot Studios: 26 units due in 13 days (pretax budget cap $191,536)
- Noble Trust: 26 units due in 14 days (pretax budget cap $189,826)
- Riverdale Lyceum: 26 units due in 14 days (pretax budget cap $189,361)

On-hand finished stock covers 36 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.2% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.2% at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
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
