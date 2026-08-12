**Priya Shah · Supply & Procurement · Teams**

All orders below for Laminar Flow Bench Horizontal need confirmed supply coverage and scheduling.

- Horizon Architects: 16 units due in 8 days (pretax budget cap $91,251)
- Peak Forum: 15 units due in 10 days (pretax budget cap $82,268)
- Conduit Collective East: 16 units due in 10 days (pretax budget cap $85,092)
- Monarch Clinics: 14 units due in 12 days (pretax budget cap $78,825)
- Metro Sciences: 17 units due in 13 days (pretax budget cap $95,567)
- Apex Workshop: 17 units due in 14 days (pretax budget cap $97,412)
- Coral Innovations: 19 units due in 14 days (pretax budget cap $100,866)
- Nimbus Studios: 22 units due in 14 days (pretax budget cap $120,295)

On-hand finished stock covers 19 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.5% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.5% at selling price.
* Finance considers the existing stock as sunk cost.
* Finished-goods procurement is not allowed for these orders because leadership has directed us to move off of external vendors; rely on in-house manufacturing instead.
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
