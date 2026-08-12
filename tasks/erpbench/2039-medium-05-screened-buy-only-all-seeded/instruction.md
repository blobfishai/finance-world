**Priya Shah · Supply & Procurement · Teams**

Confirm supply status for the latest Corner Peninsula Lab Station requests.

- Granite Guild: 20 units due in 8 days (pretax budget cap $28,042)
- Pacific Solutions Group: 14 units due in 9 days (pretax budget cap $15,763)
- Ledger Foundry: 21 units due in 9 days (pretax budget cap $28,901)
- Skyline Collective East: 22 units due in 10 days (pretax budget cap $32,475)
- Northbridge Ventures: 23 units due in 13 days (pretax budget cap $33,356)
- Scion Studios West: 21 units due in 13 days (pretax budget cap $28,668)
- Aegis Pavilion: 20 units due in 14 days (pretax budget cap $27,824)
- Crest Analytics: 17 units due in 14 days (pretax budget cap $24,967)
- Eclipse Enterprises: 26 units due in 14 days (pretax budget cap $35,994)
- Coral Academy: 16 units due in 14 days (pretax budget cap $22,084)

Current finished-goods stock is 90 units. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.9% at selling price.

## Background & Policy

* Order acceptance must follow these rules.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 21 and 25 units and allow at least 9 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Approved orders should be satisfied with the minimum necessary new spend.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 28.9% new-spend margin at selling price.
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

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
