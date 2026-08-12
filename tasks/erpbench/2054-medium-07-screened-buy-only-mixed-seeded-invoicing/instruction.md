**Priya Shah · Supply & Procurement · Teams**

Process the incoming customer orders for Rooftop Package Unit 10-Ton.

- Atlas Agency: 14 units due in 8 days (pretax budget cap $123,410)
- Citadel Academy: 19 units due in 9 days (pretax budget cap $165,038)
- Chrome Conservatory: 15 units due in 9 days (pretax budget cap $129,527)
- Riverdale Archive: 16 units due in 10 days (pretax budget cap $136,514)
- Keystone Initiative: 22 units due in 11 days (pretax budget cap $187,671)
- Cosmo Collective East: 21 units due in 12 days (pretax budget cap $192,755)
- Trellis Group: 19 units due in 14 days (pretax budget cap $161,584)
- Aegis Society: 18 units due in 14 days (pretax budget cap $162,003)

We have 68 finished units on hand. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.3% at selling price. After fulfillment, create and post the required linked customer invoices. Use 30 Days terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Customer order acceptance will be determined as follows.
* Accepted orders must request between 19 and 20 units and allow at least 11 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Deliver eligible orders but focus on reducing fresh procurement or manufacturing expenses.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.3% at selling price.
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

Work in the `odoo` ERP and commit the plan there.
