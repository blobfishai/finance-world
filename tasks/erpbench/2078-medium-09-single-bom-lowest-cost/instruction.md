**Priya Shah · Supply & Procurement · Teams**

Each customer order below requires a fulfillment-ready supply solution before its delivery due date:

- Northbridge Creative: 20 units due in 8 days (pretax budget cap $410,995)
- Titan Productions: 14 units due in 9 days (pretax budget cap $270,155)
- Stratos Reserve: 22 units due in 9 days (pretax budget cap $447,634)
- Westfield Interactive: 22 units due in 11 days (pretax budget cap $445,979)
- Equinox Bazaar: 15 units due in 11 days (pretax budget cap $306,548)
- Cedar Outfitters: 16 units due in 12 days (pretax budget cap $331,539)
- Sterling Pictures: 15 units due in 13 days (pretax budget cap $309,806)
- Monarch Workshop: 17 units due in 13 days (pretax budget cap $339,232)
- Oakmont Holdings: 18 units due in 13 days (pretax budget cap $351,788)
- Aether Archive: 21 units due in 13 days (pretax budget cap $428,929)

On-hand finished stock covers 80 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.1% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.1% at selling price.
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
* Review Internal Notes/comments on stock, customers, vendors, and workcenters before you confirm entries in the ERP.

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
