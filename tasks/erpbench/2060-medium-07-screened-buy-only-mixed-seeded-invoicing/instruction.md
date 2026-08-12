**Priya Shah · Supply & Procurement · Teams**

Fill the pending customer orders for Water-Source Heat Pump Console.

- Anvil Chambers: 16 units due in 8 days (pretax budget cap $123,007)
- Velocity Gallery: 20 units due in 8 days (pretax budget cap $149,820)
- Fairview Systems: 15 units due in 8 days (pretax budget cap $108,107)
- Keystone Exchange: 20 units due in 9 days (pretax budget cap $146,433)
- Atlas Advisory: 26 units due in 9 days (pretax budget cap $192,810)
- Riverdale Pictures: 20 units due in 13 days (pretax budget cap $147,294)
- Stonewall Labs: 18 units due in 13 days (pretax budget cap $131,836)
- Spectra Hub: 25 units due in 14 days (pretax budget cap $181,015)

We have 73 finished units on hand. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.6% at selling price. After fulfillment, create and post the required linked customer invoices. Use 30 Days terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Order acceptance must follow these rules.
* Accepted orders must request between 17 and 24 units and allow at least 10 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* After acceptance, cover each qualifying order while achieving the lowest possible new outlay.
* The combined units covered through new purchasing or manufacturing must clear at least 24.6% portfolio-level new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
* Some sales documents may already exist in draft; review existing documents before creating new ones.
* Cancel any already-drafted sales order that fails those acceptance rules.
* Customer budgets are pre-tax amounts.
* Link every accepted Sales Order to the related Purchase Orders for traceability.
* After confirming each retained sales order, create and post exactly one linked customer invoice.
* Use 30 Days terms on retained sales orders and all linked customer invoices.
* Rejected, cancelled, or skipped orders must not be invoiced.
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
