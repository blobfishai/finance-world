**Priya Shah · Supply & Procurement · Teams**

Address the current order backlog for Split System Heat Pump 5-Ton.

- Monarch Interactive: 18 units due in 9 days (pretax budget cap $100,346)
- Thornton Sciences: 18 units due in 9 days (pretax budget cap $95,542)
- Keystone Reserve: 19 units due in 10 days (pretax budget cap $107,976)
- Ivory Solutions Group: 14 units due in 10 days (pretax budget cap $76,153)
- Ashford Brands: 15 units due in 11 days (pretax budget cap $78,459)
- Spectra Workspaces: 19 units due in 12 days (pretax budget cap $107,225)
- Grove Architects: 26 units due in 12 days (pretax budget cap $143,376)
- Horizon Supply Co: 25 units due in 12 days (pretax budget cap $136,440)
- Circuit Trust: 26 units due in 13 days (pretax budget cap $142,905)

We have 78 finished units on hand. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.6% at selling price. After fulfillment, create and post the required linked customer invoices. Use 30 Days terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Customer order acceptance will be determined as follows.
* Accepted orders must request between 19 and 24 units and allow at least 12 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For every accepted order, fulfill it while keeping additional procurement or manufacturing outflow to a minimum.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 26.6% new-spend margin at selling price.
* Accounting treats the existing stock as sunk cost.
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
* Review Internal Notes/comments on stock, customers, and vendors before you confirm entries in the ERP.

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
