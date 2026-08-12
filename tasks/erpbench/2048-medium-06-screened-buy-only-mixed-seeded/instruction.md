**Priya Shah · Supply & Procurement · Teams**

Handle the list of live Serial Communication Bundle order demands.

- Eclipse Systems: 17 units due in 8 days (pretax budget cap $3,584)
- Nimbus Workspaces: 26 units due in 8 days (pretax budget cap $5,811)
- Oxide Institute: 14 units due in 11 days (pretax budget cap $2,452)
- Copper Lyceum: 19 units due in 11 days (pretax budget cap $4,240)
- Circuit Greenhouse: 17 units due in 13 days (pretax budget cap $3,759)
- Crestview Analytics: 18 units due in 14 days (pretax budget cap $3,934)
- Chrome Boutique: 16 units due in 14 days (pretax budget cap $3,514)
- Pinnacle Council: 17 units due in 14 days (pretax budget cap $3,760)

Current finished-goods stock is 58 units. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.6% at selling price.

## Background & Policy

* Customer order acceptance is based on the following criteria.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 18 and 18 units.
* Reject or cancel any order that fails those acceptance rules.
* For every order that passes acceptance, provide coverage while spending as little as possible.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.6% at selling price.
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
* Check Internal Notes/comments on stock, customers, and vendors before you release anything.

Fulfillment constraints for accepted orders:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
