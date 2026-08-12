**Priya Shah · Supply & Procurement · Teams**

Ensure all these Under-Desk Sound Shield customer orders are supplied on schedule:

- Oxide Office: 6 units due in 5 days (pretax budget cap $1,507)
- Grove Research: 12 units due in 7 days (pretax budget cap $2,958)
- Nexus Observatory: 2 units due in 9 days (pretax budget cap $484)
- Peak Bazaar: 12 units due in 9 days (pretax budget cap $2,912)

On-hand finished stock covers 26 units. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29% at selling price. After fulfillment, create and post the required linked customer invoices. Use 30 Days terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29% at selling price.
* Finance considers the existing stock as sunk cost.
* After confirming each retained sales order, create and post exactly one linked customer invoice.
* Use 30 Days terms on retained sales orders and all linked customer invoices.
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
