**Priya Shah · Supply & Procurement · Teams**

Cover all outstanding Mobile Lab Cart Workstation order requests.

- Ashford Reserve: 14 units due in 8 days (pretax budget cap $12,821)
- Prism Conservatory: 26 units due in 8 days (pretax budget cap $29,597)
- Forge Outfitters: 16 units due in 9 days (pretax budget cap $18,132)
- Alloy Greenhouse: 16 units due in 9 days (pretax budget cap $17,085)
- Trident Studios East: 21 units due in 10 days (pretax budget cap $21,918)
- Zenith Ventures: 17 units due in 12 days (pretax budget cap $18,909)
- Atlas Technologies: 20 units due in 12 days (pretax budget cap $22,557)
- Beacon Theater: 14 units due in 12 days (pretax budget cap $15,755)
- Haven Innovations: 20 units due in 13 days (pretax budget cap $21,968)
- Alpine Solutions Group: 26 units due in 13 days (pretax budget cap $29,074)

Current finished-goods stock is 89 units. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.8% at selling price.

## Background & Policy

* The rules for which orders can be accepted are outlined below.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must request between 18 and 25 units and allow at least 10 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For every accepted order, fulfill it while keeping additional procurement or manufacturing outflow to a minimum.
* The combined units covered through new purchasing or manufacturing must clear at least 28.8% portfolio-level new-spend margin at selling price.
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

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
