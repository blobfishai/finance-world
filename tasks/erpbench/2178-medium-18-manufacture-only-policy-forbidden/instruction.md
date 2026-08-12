**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Softwall Curtain Cleanroom ISO 8 require confirmed supply to proceed with fulfillment:

- Ridge Trust: 15 units due in 8 days (pretax budget cap $108,542)
- Crest Studios North: 18 units due in 8 days (pretax budget cap $137,559)
- Granite Studios: 18 units due in 8 days (pretax budget cap $131,580)
- Silverline Advisory: 14 units due in 11 days (pretax budget cap $110,311)
- Cascade Partners: 16 units due in 11 days (pretax budget cap $124,846)
- Baseline Interactive: 14 units due in 11 days (pretax budget cap $109,694)
- Fairview Collective East: 26 units due in 12 days (pretax budget cap $189,869)
- Hartland Brands: 15 units due in 13 days (pretax budget cap $116,219)

We have 25 finished units on hand.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 30% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 30% portfolio-level new-spend margin at selling price.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

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
