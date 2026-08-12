**Priya Shah · Supply & Procurement · Teams**

Ensure all these 48U High-Density Cabinet customer orders are supplied on schedule:

- Catalyst Museum: 6 units due in 6 days (pretax budget cap $10,835)
- Meridian Society: 6 units due in 7 days (pretax budget cap $11,290)
- Aegis Refinery: 12 units due in 8 days (pretax budget cap $22,924)
- Horizon Consortium: 12 units due in 9 days (pretax budget cap $21,679)

Current finished-goods stock is 30 units. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.1% at selling price. After fulfillment, create and post the required linked customer invoices. Use Immediate Payment terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Get every customer order covered without violating any stated policy or constraint.
* The combined units covered through new purchasing or manufacturing must clear at least 26.1% portfolio-level new-spend margin at selling price.
* Finished stock is available and may be used where it helps satisfy the stated constraints.
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
* Review Internal Notes/comments on stock, customers, and vendors before you confirm entries in the ERP.

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
