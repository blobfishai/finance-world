**Priya Shah · Supply & Procurement · Teams**

The following CO2 Total Flooding System customer orders are firm and must be supplied on schedule:

- Stratos Ventures: 19 units due in 8 days (pretax budget cap $204,655)
- Ridgeline Workshop: 18 units due in 8 days (pretax budget cap $189,105)
- Cosmo Sciences: 23 units due in 8 days (pretax budget cap $248,476)
- Opal Workspaces: 19 units due in 8 days (pretax budget cap $215,639)
- Mosaic Robotics: 19 units due in 8 days (pretax budget cap $216,154)
- Haven Architects: 18 units due in 9 days (pretax budget cap $193,027)
- Metro Institute: 18 units due in 9 days (pretax budget cap $201,929)
- Coral Guild: 18 units due in 9 days (pretax budget cap $200,714)
- Indigo Greenhouse: 23 units due in 9 days (pretax budget cap $254,118)
- Raven Systems: 21 units due in 9 days (pretax budget cap $221,911)
- Cedar Manufactory: 19 units due in 9 days (pretax budget cap $210,931)
- Lakewood Dynamics: 27 units due in 10 days (pretax budget cap $299,453)
- Ivory Research: 20 units due in 10 days (pretax budget cap $212,171)
- Arrow Media: 18 units due in 10 days (pretax budget cap $205,840)
- Eclipse Academy: 18 units due in 10 days (pretax budget cap $192,924)
- Borough Alliance: 20 units due in 11 days (pretax budget cap $216,826)
- Ironside Advisory: 19 units due in 12 days (pretax budget cap $218,086)
- Bayshore Enterprises: 21 units due in 12 days (pretax budget cap $220,585)
- Axis Clinics: 19 units due in 12 days (pretax budget cap $201,564)
- Alpine Supply Co: 24 units due in 13 days (pretax budget cap $264,766)
- Zenith Reserve: 19 units due in 13 days (pretax budget cap $212,397)
- Nimbus Studios: 19 units due in 13 days (pretax budget cap $208,894)
- Sapphire Observatory: 18 units due in 13 days (pretax budget cap $205,336)
- Citadel Collective: 23 units due in 13 days (pretax budget cap $244,037)
- Summit Interactive: 20 units due in 13 days (pretax budget cap $217,406)

On-hand finished stock covers 200 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.9% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.9% new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
* You must create and confirm the necessary sales orders, purchase orders, and/or manufacturing orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* For subassembly or intermediate MOs, put the immediate parent MO reference(s) that the subassembly feeds (e.g. WH/MO/00020 or WH/MO/00020, WH/MO/00021) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> (Subassembly MO if needed) -> PO or SO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* If you choose to manufacture, you must procure the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

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
