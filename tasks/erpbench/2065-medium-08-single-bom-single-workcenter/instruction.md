**Priya Shah · Supply & Procurement · Teams**

Prepare a fulfillment strategy for all listed High-Bay LED Fixture 200W orders to meet due dates and avoid shortages.

- Axis Conservatory: 17 units due in 8 days (pretax budget cap $9,719)
- Aegis Consortium: 14 units due in 8 days (pretax budget cap $8,289)
- Brookfield Designs: 22 units due in 9 days (pretax budget cap $12,782)
- Alloy Publishing: 23 units due in 9 days (pretax budget cap $12,611)
- Compass Innovations: 26 units due in 9 days (pretax budget cap $14,768)
- Equinox Systems: 15 units due in 9 days (pretax budget cap $8,711)
- Aurora Academy: 18 units due in 11 days (pretax budget cap $10,651)
- Oxide Group: 18 units due in 12 days (pretax budget cap $10,759)
- Monarch Hub: 24 units due in 12 days (pretax budget cap $13,425)
- Element Dynamics: 23 units due in 12 days (pretax budget cap $13,467)

Current finished-goods stock is 99 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.8% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 27.8% portfolio-level new-spend margin at selling price.
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

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
