**Priya Shah · Supply & Procurement · Teams**

Start with the live customer requests for Sensor Cable Harness.

- Stonewall Office: 15 units due in 10 days (pretax budget cap $3,723)
- Ironside Innovations: 15 units due in 11 days (pretax budget cap $3,787)
- Pivot Outfitters: 20 units due in 11 days (pretax budget cap $4,904)
- Axis Solutions Group: 18 units due in 12 days (pretax budget cap $4,624)
- Westfield Academy: 20 units due in 13 days (pretax budget cap $5,055)
- Monarch Theater: 14 units due in 13 days (pretax budget cap $2,902)
- Dune Labs: 21 units due in 14 days (pretax budget cap $5,277)
- Granite Chambers: 21 units due in 14 days (pretax budget cap $5,403)

We have 63 finished units on hand. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.7% at selling price.

## Background & Policy

* These are the rules for customer order acceptance.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 16 and 20 units.
* Reject or cancel any order that fails those acceptance rules.
* Arrange supply for eligible orders, ensuring the least new investment.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 25.7% new-spend margin at selling price.
* Accounting treats the existing stock as sunk cost.
* Some sales documents may already exist in draft; review existing documents before creating new ones.
* Cancel any already-drafted sales order that fails those acceptance rules.
* Customer budgets are pre-tax amounts.
* Link every accepted Sales Order to the related Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> PO for every incoming customer order you accept.
* You must sell this product at List Price.
* On every accepted Sales Order, set the commitment date.
* On purchase orders, you must set the delivery date.
* Before releasing anything, read the Internal Notes/comments on stock, customers, and vendors.

Fulfillment constraints for accepted orders:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
