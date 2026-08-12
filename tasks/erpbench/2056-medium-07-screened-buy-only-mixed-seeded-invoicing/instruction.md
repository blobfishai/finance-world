**Priya Shah · Supply & Procurement · Teams**

Review the open order requests for Packaged Terminal Air Conditioner.

- Alloy Theater: 16 units due in 8 days (pretax budget cap $32,327)
- Alpine Chambers: 19 units due in 8 days (pretax budget cap $38,344)
- Scion Observatory: 14 units due in 8 days (pretax budget cap $28,233)
- Terra Studios West: 26 units due in 10 days (pretax budget cap $50,281)
- Spectra Clinics: 18 units due in 11 days (pretax budget cap $36,977)
- Cascade Guild: 17 units due in 12 days (pretax budget cap $33,477)
- Nexus Media: 20 units due in 13 days (pretax budget cap $38,663)
- Millbrook Systems: 22 units due in 14 days (pretax budget cap $45,752)

We have 76 finished units on hand. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.6% at selling price. After fulfillment, create and post the required linked customer invoices. Use 30 Days terms on retained sales orders and all linked customer invoices.

## Background & Policy

* These are the rules for customer order acceptance.
* Accepted orders must request between 18 and 21 units and allow at least 13 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For all accepted orders, arrange fulfillment at the lowest possible new purchase or manufacturing cost.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 25.6% new-spend margin at selling price.
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

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
