**Priya Shah · Supply & Procurement · Teams**

Start with the live customer requests for Hybrid Fiber-Copper Assembly.

- Polar Bureau: 15 units due in 8 days (pretax budget cap $9,509)
- Sierra Practice: 20 units due in 9 days (pretax budget cap $12,443)
- Matrix Arena: 24 units due in 9 days (pretax budget cap $15,674)
- Keystone Dynamics: 15 units due in 10 days (pretax budget cap $10,090)
- Element Designs: 25 units due in 11 days (pretax budget cap $15,691)
- Alpine Advisory: 14 units due in 11 days (pretax budget cap $6,597)
- Granite Studios: 20 units due in 12 days (pretax budget cap $13,134)
- Conduit Greenhouse: 19 units due in 13 days (pretax budget cap $12,428)

Current finished-goods stock is 63 units. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.4% at selling price.

## Background & Policy

* Customer order acceptance is based on the following criteria.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 15 and 23 units.
* Reject or cancel any order that fails those acceptance rules.
* For qualifying orders, ensure fulfillment while keeping new costs down.
* The combined units covered through new purchasing or manufacturing must clear at least 27.4% portfolio-level new-spend margin at selling price.
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
