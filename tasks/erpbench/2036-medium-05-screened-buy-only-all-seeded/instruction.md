**Priya Shah · Supply & Procurement · Teams**

Handle the list of live Laboratory Work Bench order demands.

- Cardinal Forum: 26 units due in 8 days (pretax budget cap $39,556)
- Flint Museum: 14 units due in 9 days (pretax budget cap $16,131)
- Ridge Hub: 17 units due in 10 days (pretax budget cap $25,742)
- Crown Research: 26 units due in 11 days (pretax budget cap $41,895)
- Vantage Theater: 25 units due in 11 days (pretax budget cap $38,027)
- Marble Collective East: 17 units due in 12 days (pretax budget cap $26,998)
- Redstone Boutique: 16 units due in 12 days (pretax budget cap $24,512)
- Gateway Practice: 14 units due in 12 days (pretax budget cap $21,410)
- Quartz Pictures: 25 units due in 13 days (pretax budget cap $40,364)

We have 84 finished units on hand. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.5% at selling price.

## Background & Policy

* The rules for which orders can be accepted are outlined below.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 15 and 24 units and allow at least 9 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For every order that passes acceptance, provide coverage while spending as little as possible.
* The combined units covered through new purchasing or manufacturing must clear at least 27.5% portfolio-level new-spend margin at selling price.
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
