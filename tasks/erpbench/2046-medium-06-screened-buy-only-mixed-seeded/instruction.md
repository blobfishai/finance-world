**Priya Shah · Supply & Procurement · Teams**

Address the current order backlog for High-Voltage Power Cable Set.

- Ivory Foundry: 17 units due in 8 days (pretax budget cap $11,462)
- Crestview Museum: 14 units due in 10 days (pretax budget cap $6,599)
- Crown Atelier: 15 units due in 11 days (pretax budget cap $10,607)
- Dune Technologies: 15 units due in 12 days (pretax budget cap $10,111)
- Oakmont Designs: 20 units due in 12 days (pretax budget cap $13,838)
- Oxide Practice: 24 units due in 12 days (pretax budget cap $16,429)
- Alpine Collective: 15 units due in 12 days (pretax budget cap $9,848)
- Equinox Bureau: 25 units due in 14 days (pretax budget cap $17,060)
- Opal Guild: 17 units due in 14 days (pretax budget cap $11,743)

We have 77 finished units on hand. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.3% at selling price.

## Background & Policy

* Customer order acceptance is based on the following criteria.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 21 and 24 units.
* Reject or cancel any order that fails those acceptance rules.
* After acceptance, cover each qualifying order while achieving the lowest possible new outlay.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.3% at selling price.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, and vendors.

Fulfillment constraints for accepted orders:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
