**Priya Shah · Supply & Procurement · Teams**

Prepare a fulfillment strategy for all listed Chemical Storage Safety Cabinet orders to meet due dates and avoid shortages.

- Ridgeline Systems: 16 units due in 8 days (pretax budget cap $30,970)
- Polar Society: 19 units due in 11 days (pretax budget cap $40,272)
- Thornton Holdings: 16 units due in 12 days (pretax budget cap $32,416)
- Redstone Trust: 15 units due in 12 days (pretax budget cap $30,798)
- Citadel Interactive: 20 units due in 13 days (pretax budget cap $38,662)
- Stratos Studios South: 24 units due in 14 days (pretax budget cap $47,299)
- Flint Bureau: 22 units due in 14 days (pretax budget cap $45,770)
- Cipher Boutique: 16 units due in 14 days (pretax budget cap $32,547)
- Ashford Studios North: 14 units due in 14 days (pretax budget cap $29,345)

Current finished-goods stock is 79 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.3% at selling price.

## Background & Policy

* Get every customer order covered while keeping as much shared workcenter capacity open as possible. Keep new purchasing and manufacturing spend as low as possible when workcenter-capacity use ties.
* The combined units covered through new purchasing or manufacturing must clear at least 29.3% portfolio-level new-spend margin at selling price.
* Use available finished stock where it helps preserve shared workcenter capacity.
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
