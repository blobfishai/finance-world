**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Dust Containment Enclosure require confirmed supply to proceed with fulfillment:

- Polar Forum: 26 units due in 8 days (pretax budget cap $87,206)
- Gateway Reserve: 24 units due in 8 days (pretax budget cap $81,715)
- Trellis Studios West: 21 units due in 9 days (pretax budget cap $71,336)
- Lumen Gallery: 19 units due in 9 days (pretax budget cap $65,898)
- Cascade Alliance: 26 units due in 9 days (pretax budget cap $87,199)
- Terra Research: 18 units due in 11 days (pretax budget cap $58,962)
- Alloy Trust: 21 units due in 11 days (pretax budget cap $72,753)
- Crown Labs: 26 units due in 11 days (pretax budget cap $91,728)
- Equinox Studios South: 24 units due in 12 days (pretax budget cap $84,720)
- Jade Engineering: 25 units due in 13 days (pretax budget cap $83,087)

We have 104 finished units on hand. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.8% at selling price.

## Background & Policy

* Get every customer order covered while keeping as much shared workcenter capacity open as possible. Keep new purchasing and manufacturing spend as low as possible when workcenter-capacity use ties.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.8% at selling price.
* Use the finished stock on hand where it helps reduce demand on shared workcenters.
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

Work in the `odoo` ERP and commit the plan there.
