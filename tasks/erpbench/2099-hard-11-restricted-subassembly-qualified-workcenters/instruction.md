**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Portable Solar Generator Kit require confirmed supply to proceed with fulfillment:

- Lumen Conservatory: 16 units due in 9 days (pretax budget cap $32,041)
- Monarch Collective East: 14 units due in 9 days (pretax budget cap $28,040)
- Chrome Collective: 14 units due in 9 days (pretax budget cap $28,271)
- Axis Labs: 19 units due in 11 days (pretax budget cap $41,156)
- Jade Creative: 24 units due in 11 days (pretax budget cap $51,710)
- Compass Theater: 19 units due in 11 days (pretax budget cap $38,814)
- Osprey Museum: 14 units due in 12 days (pretax budget cap $29,181)
- Quantum Agency: 21 units due in 12 days (pretax budget cap $43,904)
- Echo Reserve: 15 units due in 12 days (pretax budget cap $30,516)
- Beacon Greenhouse: 14 units due in 14 days (pretax budget cap $29,446)

On-hand finished stock covers 38 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.1% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.1% at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
* You must create and confirm the necessary sales orders, purchase orders, and/or manufacturing orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* For subassembly or intermediate MOs, put the immediate parent MO reference(s) that the subassembly feeds (e.g. WH/MO/00020 or WH/MO/00020, WH/MO/00021) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> (Subassembly MO if needed) -> PO or SO -> PO.
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

Work in the `odoo` ERP and commit the plan there.
