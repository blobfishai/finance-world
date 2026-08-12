**Priya Shah · Supply & Procurement · Teams**

All orders below for Gearless Traction Controller 10-Stop need confirmed supply coverage and scheduling.

- Zenith Technologies: 15 units due in 9 days (pretax budget cap $144,993)
- Eclipse Council: 14 units due in 9 days (pretax budget cap $127,911)
- Raven Clinics: 15 units due in 10 days (pretax budget cap $146,314)
- Ironwood Interactive: 14 units due in 11 days (pretax budget cap $137,330)
- Helix Theater: 14 units due in 12 days (pretax budget cap $138,135)
- Conduit Works: 18 units due in 12 days (pretax budget cap $164,250)
- Arc Outfitters: 25 units due in 12 days (pretax budget cap $235,629)
- Anvil Office: 17 units due in 13 days (pretax budget cap $164,987)
- Nimbus Academy: 21 units due in 14 days (pretax budget cap $197,751)

On-hand finished stock covers 80 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.4% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.4% at selling price.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
