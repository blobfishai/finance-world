**Priya Shah · Supply & Procurement · Teams**

Each customer order below requires a fulfillment-ready supply solution before its delivery due date:

- Crest Guild: 9 units due in 7 days (pretax budget cap $4,356)
- Bronze Boutique: 12 units due in 8 days (pretax budget cap $5,891)
- Catalyst Enterprises: 4 units due in 9 days (pretax budget cap $2,041)
- Pacific Bureau: 11 units due in 9 days (pretax budget cap $5,461)

We have 29 finished units on hand. You cannot build the finished product internally, so any gap beyond stock has to be covered by purchasing.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.5% at selling price.

## Background & Policy

* Fulfill all customer orders while respecting all stated policies and constraints.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 26.5% new-spend margin at selling price.
* Finished stock is available and may be used where it helps satisfy the stated constraints.
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
