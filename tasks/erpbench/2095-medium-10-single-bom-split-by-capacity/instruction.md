**Priya Shah · Supply & Procurement · Teams**

All orders below for Interlocked Access Gate Panel need confirmed supply coverage and scheduling.

- Flux Collective East: 14 units due in 9 days (pretax budget cap $25,679)
- Spark Studios: 17 units due in 9 days (pretax budget cap $31,137)
- Keystone Gallery: 15 units due in 10 days (pretax budget cap $29,133)
- Pacific Hub: 17 units due in 11 days (pretax budget cap $33,480)
- Raven Reserve: 19 units due in 11 days (pretax budget cap $37,821)
- Skyline Refinery: 14 units due in 12 days (pretax budget cap $26,819)
- Lakewood Pavilion: 17 units due in 14 days (pretax budget cap $31,884)
- Gateway Labs: 23 units due in 14 days (pretax budget cap $43,601)
- Baltic Academy: 26 units due in 14 days (pretax budget cap $50,113)

Current finished-goods stock is 68 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.6% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.6% new-spend margin at selling price.
* Available finished stock can be used where it helps keep shared workcenter capacity open.
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

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
