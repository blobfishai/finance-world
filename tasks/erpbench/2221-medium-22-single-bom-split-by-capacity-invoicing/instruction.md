**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Chemical Storage Safety Cabinet require confirmed supply to proceed with fulfillment:

- Granite Fabricators: 15 units due in 8 days (pretax budget cap $31,629)
- Stonewall Guild: 26 units due in 8 days (pretax budget cap $53,994)
- Stratos Hub: 20 units due in 9 days (pretax budget cap $40,921)
- Equinox Boutique: 17 units due in 10 days (pretax budget cap $36,191)
- Cobalt Workspaces: 26 units due in 12 days (pretax budget cap $51,771)
- Drift Refinery: 26 units due in 12 days (pretax budget cap $52,778)
- Spire Foundry: 17 units due in 13 days (pretax budget cap $35,632)
- Ridgeline Pavilion: 22 units due in 14 days (pretax budget cap $43,644)
- Borough Atelier: 16 units due in 14 days (pretax budget cap $32,115)
- Lumen Systems: 25 units due in 14 days (pretax budget cap $52,845)

On-hand finished stock covers 100 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.1% at selling price. After fulfillment, create and post the required linked customer invoices. Use Immediate Payment terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.1% at selling price.
* Accounting treats the existing stock as sunk cost.
* After confirming each retained sales order, create and post exactly one linked customer invoice.
* Use Immediate Payment terms on retained sales orders and all linked customer invoices.
* You must create and confirm the necessary sales orders, purchase orders, and/or manufacturing orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> PO or SO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* If you choose to manufacture, you must procure the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
