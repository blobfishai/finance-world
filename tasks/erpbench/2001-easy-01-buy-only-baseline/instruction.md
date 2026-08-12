**Priya Shah · Supply & Procurement · Teams**

Ensure all these Door Seal Acoustic Kit customer orders are supplied on schedule:

- Arrow Works: 8 units due in 6 days (pretax budget cap $1,529)
- Evergreen Observatory: 12 units due in 7 days (pretax budget cap $2,287)
- Peak Lyceum: 12 units due in 8 days (pretax budget cap $2,399)
- Summit Studios North: 12 units due in 9 days (pretax budget cap $2,351)

On-hand finished stock covers 38 units. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.2% at selling price.

## Background & Policy

* Cover every customer order while following all stated policies and constraints.
* The combined units covered through new purchasing or manufacturing must clear at least 29.2% portfolio-level new-spend margin at selling price.
* Available finished stock may be used wherever it helps achieve a constraint-compliant plan.
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
