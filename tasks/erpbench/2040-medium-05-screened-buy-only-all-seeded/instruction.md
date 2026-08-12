**Priya Shah · Supply & Procurement · Teams**

Handle the open Wet Lab Sink Bench order queue.

- Eclipse Boutique: 26 units due in 9 days (pretax budget cap $55,044)
- Echo Alliance: 24 units due in 10 days (pretax budget cap $52,327)
- Fairview Designs: 14 units due in 11 days (pretax budget cap $30,300)
- Thornton Studios East: 14 units due in 11 days (pretax budget cap $22,395)
- Citadel Museum: 16 units due in 11 days (pretax budget cap $34,292)
- Peak Studios South: 15 units due in 12 days (pretax budget cap $33,029)
- Nexus Partners: 16 units due in 12 days (pretax budget cap $34,367)
- Beacon Supply Co: 17 units due in 12 days (pretax budget cap $37,577)
- Silverline Research: 22 units due in 14 days (pretax budget cap $48,133)
- Nimbus Group: 26 units due in 14 days (pretax budget cap $56,399)

Current finished-goods stock is 82 units. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.5% at selling price.

## Background & Policy

* Customer order acceptance will be determined as follows.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 17 and 23 units and allow at least 10 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For every accepted order, fulfill it while keeping additional procurement or manufacturing outflow to a minimum.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 24.5% new-spend margin at selling price.
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
* Check Internal Notes/comments on stock, customers, and vendors before you release anything.

Fulfillment constraints for accepted orders:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
