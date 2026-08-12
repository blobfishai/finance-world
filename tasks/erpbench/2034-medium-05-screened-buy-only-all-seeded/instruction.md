**Priya Shah · Supply & Procurement · Teams**

Review the open order requests for Laboratory Work Bench.

- Oxide Architects: 17 units due in 8 days (pretax budget cap $24,926)
- Spectra Guild: 23 units due in 8 days (pretax budget cap $34,492)
- Titan Reserve: 15 units due in 10 days (pretax budget cap $22,566)
- Jade Bazaar: 14 units due in 11 days (pretax budget cap $17,139)
- Bronze Interactive: 16 units due in 11 days (pretax budget cap $24,842)
- Raven Institute: 14 units due in 13 days (pretax budget cap $21,282)
- Stonewall Atelier: 23 units due in 14 days (pretax budget cap $34,561)
- Conduit Lyceum: 14 units due in 14 days (pretax budget cap $20,120)
- Spire Archive: 17 units due in 14 days (pretax budget cap $24,415)

Current finished-goods stock is 67 units. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.7% at selling price.

## Background & Policy

* Order acceptance must follow these rules.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 17 and 22 units and allow at least 14 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For qualifying orders, ensure fulfillment while keeping new costs down.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 24.7% new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
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
