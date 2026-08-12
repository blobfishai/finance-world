**Priya Shah · Supply & Procurement · Teams**

Plan fulfillment for these outstanding Curved Diffuser Panel orders to ensure timely deliveries:

- Prism Manufactory: 8 units due in 5 days (pretax budget cap $4,251)
- Trident Dynamics: 12 units due in 5 days (pretax budget cap $6,483)
- Peak Systems: 12 units due in 6 days (pretax budget cap $6,355)
- Clearwater Brands: 12 units due in 7 days (pretax budget cap $6,484)

We have 38 finished units on hand. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.2% at selling price.

## Background & Policy

* Cover every customer order while following all stated policies and constraints.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 28.2% new-spend margin at selling price.
* Finished stock is available and may be used where it helps satisfy the stated constraints.
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
