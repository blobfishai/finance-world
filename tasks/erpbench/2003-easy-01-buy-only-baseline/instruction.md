**Priya Shah · Supply & Procurement · Teams**

Prepare a fulfillment strategy for all listed Under-Desk Sound Shield orders to meet due dates and avoid shortages.

- Stonewall Designs: 12 units due in 5 days (pretax budget cap $3,089)
- Terra Forum: 4 units due in 8 days (pretax budget cap $1,021)
- Arc Office: 12 units due in 9 days (pretax budget cap $3,290)
- Vantage Hub: 12 units due in 9 days (pretax budget cap $3,239)

On-hand finished stock covers 34 units. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.9% at selling price.

## Background & Policy

* Get every customer order covered without violating any stated policy or constraint.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 24.9% new-spend margin at selling price.
* Use the finished stock on hand where it helps satisfy the stated policies and constraints.
* You must create and confirm the necessary sales orders and purchase orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On purchase orders, you must set the delivery date.
* Check Internal Notes/comments on stock, customers, and vendors before you release anything.

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
