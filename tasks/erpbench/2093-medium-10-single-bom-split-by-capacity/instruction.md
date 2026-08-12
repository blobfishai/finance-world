**Priya Shah · Supply & Procurement · Teams**

The following Laser Safety Curtain System customer orders are firm and must be supplied on schedule:

- Noble Guild: 14 units due in 8 days (pretax budget cap $42,648)
- Borough Studios West: 21 units due in 8 days (pretax budget cap $61,984)
- Raven Labs: 15 units due in 9 days (pretax budget cap $43,495)
- Bridgeway Conservatory: 14 units due in 10 days (pretax budget cap $41,182)
- Mosaic Systems: 14 units due in 10 days (pretax budget cap $40,218)
- Lance Institute: 14 units due in 10 days (pretax budget cap $42,495)
- Catalyst Observatory: 15 units due in 13 days (pretax budget cap $43,272)
- Cobalt Exchange: 14 units due in 13 days (pretax budget cap $40,160)
- Matrix Holdings: 14 units due in 14 days (pretax budget cap $40,684)
- Spectra Solutions Group: 15 units due in 14 days (pretax budget cap $43,294)

Current finished-goods stock is 69 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.2% at selling price.

## Background & Policy

* Cover every customer order while using as little shared workcenter capacity as practical. If multiple feasible plans use the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.2% at selling price.
* Use available finished stock where it helps preserve shared workcenter capacity.
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
