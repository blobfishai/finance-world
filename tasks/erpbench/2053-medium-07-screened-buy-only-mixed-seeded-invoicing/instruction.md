**Priya Shah · Supply & Procurement · Teams**

Review the open order requests for Split System Heat Pump 5-Ton.

- Crestview Society: 17 units due in 8 days (pretax budget cap $90,781)
- Chrome Studios West: 17 units due in 9 days (pretax budget cap $98,952)
- Element Chambers: 16 units due in 9 days (pretax budget cap $86,224)
- Drift Gallery: 19 units due in 9 days (pretax budget cap $109,554)
- Spire Theater: 14 units due in 11 days (pretax budget cap $79,232)
- Horizon Guild: 16 units due in 11 days (pretax budget cap $92,359)
- Ridge Trust: 15 units due in 13 days (pretax budget cap $79,960)
- Spark Conservatory: 22 units due in 13 days (pretax budget cap $123,932)
- Nimbus Ventures: 17 units due in 14 days (pretax budget cap $93,814)

On-hand finished stock covers 67 units. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.1% at selling price. After fulfillment, create and post the required linked customer invoices. Use 30 Days terms on retained sales orders and all linked customer invoices.

## Background & Policy

* These are the rules for customer order acceptance.
* Accepted orders must request between 17 and 21 units and allow at least 12 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For every accepted order, fulfill it while keeping additional procurement or manufacturing outflow to a minimum.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.1% new-spend margin at selling price.
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
