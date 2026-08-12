**Priya Shah · Supply & Procurement · Teams**

Process the incoming customer orders for Packaged Terminal Air Conditioner.

- Opal Engineering: 15 units due in 8 days (pretax budget cap $31,483)
- Quartz Workspaces: 15 units due in 8 days (pretax budget cap $33,568)
- Comet Supply Co: 14 units due in 9 days (pretax budget cap $31,012)
- Ivory Labs: 19 units due in 11 days (pretax budget cap $40,397)
- Peak Hub: 15 units due in 11 days (pretax budget cap $33,480)
- Titan Holdings: 16 units due in 12 days (pretax budget cap $35,563)
- Drift Arena: 16 units due in 13 days (pretax budget cap $33,848)
- Raven Technologies: 26 units due in 14 days (pretax budget cap $56,059)

Current finished-goods stock is 63 units. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.5% at selling price. After fulfillment, create and post the required linked customer invoices. Use 30 Days terms on retained sales orders and all linked customer invoices.

## Background & Policy

* These are the rules for customer order acceptance.
* Accepted orders must request between 16 and 25 units and allow at least 10 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For qualifying orders, ensure fulfillment while keeping new costs down.
* The combined units covered through new purchasing or manufacturing must clear at least 26.5% portfolio-level new-spend margin at selling price.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, and vendors.

Fulfillment constraints for accepted orders:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
