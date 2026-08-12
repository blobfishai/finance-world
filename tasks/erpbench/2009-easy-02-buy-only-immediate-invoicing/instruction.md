**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Co-Location Cage Rack 42U require confirmed supply to proceed with fulfillment:

- Ironwood Reserve: 1 unit due in 5 days (pretax budget cap $3,130)
- Anvil Lyceum: 12 units due in 5 days (pretax budget cap $38,077)
- Spectra Institute: 12 units due in 7 days (pretax budget cap $37,488)
- Axis Bureau: 11 units due in 8 days (pretax budget cap $35,694)

We have 30 finished units on hand. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.5% at selling price. After fulfillment, create and post the required linked customer invoices. Use Immediate Payment terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Cover every customer order while following all stated policies and constraints.
* The combined units covered through new purchasing or manufacturing must clear at least 26.5% portfolio-level new-spend margin at selling price.
* Use the finished stock on hand where it helps satisfy the stated policies and constraints.
* After confirming each retained sales order, create and post exactly one linked customer invoice.
* Use Immediate Payment terms on retained sales orders and all linked customer invoices.
* You must create and confirm the necessary sales orders and purchase orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On purchase orders, you must set the delivery date.
* Before releasing anything, read the Internal Notes/comments on stock, customers, and vendors.

Capacity constraints:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
