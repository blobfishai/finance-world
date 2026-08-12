**Priya Shah · Supply & Procurement · Teams**

Supply plans must be created to fulfill each outstanding Acoustic Isolation Booth customer order listed.

- Aegis Hub: 15 units due in 8 days (pretax budget cap $84,779)
- Monarch Theater: 21 units due in 9 days (pretax budget cap $120,124)
- Borough Publishing: 14 units due in 11 days (pretax budget cap $79,868)
- Haven Alliance: 14 units due in 11 days (pretax budget cap $77,379)
- Solace Foundry: 26 units due in 11 days (pretax budget cap $145,212)
- Cedar Practice: 26 units due in 12 days (pretax budget cap $150,436)
- Titan Trust: 26 units due in 13 days (pretax budget cap $147,136)
- Terra Observatory: 26 units due in 13 days (pretax budget cap $146,142)
- Gateway Bazaar: 26 units due in 13 days (pretax budget cap $150,411)
- Westfield Labs: 26 units due in 14 days (pretax budget cap $150,773)

We have 97 finished units on hand. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.8% at selling price. After fulfillment, create and post the required linked customer invoices. Use Immediate Payment terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.8% at selling price.
* Accounting treats the existing stock as sunk cost.
* After confirming each retained sales order, create and post exactly one linked customer invoice.
* Use Immediate Payment terms on retained sales orders and all linked customer invoices.
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

Work in the `odoo` ERP and commit the plan there.
