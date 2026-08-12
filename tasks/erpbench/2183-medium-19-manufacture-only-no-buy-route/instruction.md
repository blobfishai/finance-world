**Priya Shah · Supply & Procurement · Teams**

Ensure all these Vertical Storing Dock Leveler customer orders are supplied on schedule:

- Chrome Collective: 18 units due in 8 days (pretax budget cap $162,859)
- Prism Studios North: 19 units due in 8 days (pretax budget cap $175,400)
- Raven Creative: 26 units due in 8 days (pretax budget cap $246,020)
- Grove Interactive: 26 units due in 8 days (pretax budget cap $254,395)
- Beacon Solutions Group: 19 units due in 8 days (pretax budget cap $181,711)
- Cascade Atelier: 24 units due in 11 days (pretax budget cap $217,599)
- Matrix Conservatory: 17 units due in 13 days (pretax budget cap $163,386)
- Noble Chambers: 14 units due in 13 days (pretax budget cap $138,035)
- Gateway Fabricators: 21 units due in 14 days (pretax budget cap $192,318)
- Lumen Bazaar: 26 units due in 14 days (pretax budget cap $234,056)

On-hand finished stock covers 33 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.6% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.6% at selling price.
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

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
