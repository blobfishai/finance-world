**Priya Shah · Supply & Procurement · Teams**

Handle the list of live Coaxial Trunk Harness order demands.

- Velocity Sciences: 15 units due in 8 days (pretax budget cap $6,914)
- Pinnacle Ventures: 15 units due in 8 days (pretax budget cap $7,323)
- Silverline Conservatory: 14 units due in 9 days (pretax budget cap $5,391)
- Spire Collective: 21 units due in 11 days (pretax budget cap $10,081)
- Monarch Technologies: 25 units due in 12 days (pretax budget cap $12,306)
- Crestview Observatory: 26 units due in 12 days (pretax budget cap $11,939)
- Keystone Solutions Group: 26 units due in 12 days (pretax budget cap $12,604)
- Catalyst Workspaces: 26 units due in 13 days (pretax budget cap $12,440)

We have 81 finished units on hand. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28% at selling price.

## Background & Policy

* Customer order acceptance will be determined as follows.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 15 and 25 units.
* Reject or cancel any order that fails those acceptance rules.
* Once orders are accepted, minimize new procurement or production spend while covering them.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 28% new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
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
