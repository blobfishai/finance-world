**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Point-of-Use Dispenser Module require confirmed supply to proceed with fulfillment:

- Cedar Greenhouse: 22 units due in 9 days (pretax budget cap $20,505)
- Gateway Trading Co: 19 units due in 10 days (pretax budget cap $17,891)
- Noble Sciences: 14 units due in 11 days (pretax budget cap $13,348)
- Matrix Bazaar: 14 units due in 12 days (pretax budget cap $12,373)
- Sterling Engineering: 15 units due in 12 days (pretax budget cap $13,422)
- Stratos Pavilion: 18 units due in 12 days (pretax budget cap $16,446)
- Indigo Refinery: 15 units due in 12 days (pretax budget cap $13,616)
- Ironwood Initiative: 23 units due in 13 days (pretax budget cap $21,314)
- Sapphire Productions: 16 units due in 13 days (pretax budget cap $14,871)
- Aegis Labs: 14 units due in 14 days (pretax budget cap $13,349)

On-hand finished stock covers 89 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.3% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.3% at selling price.
* Finance considers the existing stock as sunk cost.
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
