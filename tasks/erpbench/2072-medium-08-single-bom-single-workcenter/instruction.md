**Priya Shah · Supply & Procurement · Teams**

The following customer orders for High-Bay LED Fixture 200W require confirmed supply to proceed with fulfillment:

- Metro Brands: 14 units due in 8 days (pretax budget cap $7,969)
- Sterling Reserve: 17 units due in 8 days (pretax budget cap $9,727)
- Coral Collective East: 14 units due in 8 days (pretax budget cap $7,825)
- Solace Bazaar: 16 units due in 9 days (pretax budget cap $9,115)
- Redstone Archive: 16 units due in 9 days (pretax budget cap $9,226)
- Zenith Hub: 16 units due in 9 days (pretax budget cap $9,150)
- Axis Lyceum: 26 units due in 10 days (pretax budget cap $14,931)
- Peak Office: 18 units due in 11 days (pretax budget cap $9,938)
- Bronze Workspaces: 22 units due in 11 days (pretax budget cap $12,991)
- Arrow Advisory: 21 units due in 11 days (pretax budget cap $12,542)

We have 77 finished units on hand. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.9% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.9% at selling price.
* Accounting treats the existing stock as sunk cost.
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

Work in the `odoo` ERP and commit the plan there.
