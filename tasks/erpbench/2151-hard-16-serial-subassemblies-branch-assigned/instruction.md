**Priya Shah · Supply & Procurement · Teams**

Ensure all these Centrifugal Compressor 200HP customer orders are supplied on schedule:

- Titan Workspaces: 24 units due in 8 days (pretax budget cap $1,243,258)
- Comet Clinics: 18 units due in 8 days (pretax budget cap $972,288)
- Copper Outfitters: 21 units due in 8 days (pretax budget cap $1,060,316)
- Ridgeline Ventures: 30 units due in 8 days (pretax budget cap $1,601,637)
- Pinnacle Engineering: 32 units due in 9 days (pretax budget cap $1,647,937)
- Stratos Theater: 25 units due in 9 days (pretax budget cap $1,346,785)
- Velocity Collective East: 29 units due in 9 days (pretax budget cap $1,559,302)
- Conduit Lyceum: 21 units due in 9 days (pretax budget cap $1,053,210)
- Metro Society: 22 units due in 9 days (pretax budget cap $1,172,594)
- Solace Architects: 21 units due in 10 days (pretax budget cap $1,120,934)
- Thornton Alliance: 21 units due in 11 days (pretax budget cap $1,094,630)
- Spark Bureau: 18 units due in 11 days (pretax budget cap $976,611)
- Quantum Innovations: 20 units due in 11 days (pretax budget cap $1,065,587)
- Granite Research: 23 units due in 11 days (pretax budget cap $1,179,149)
- Ridge Media: 18 units due in 13 days (pretax budget cap $922,718)
- Clearwater Studios East: 22 units due in 13 days (pretax budget cap $1,155,520)
- Evergreen Practice: 28 units due in 13 days (pretax budget cap $1,419,169)
- Ashford Designs: 23 units due in 13 days (pretax budget cap $1,209,226)
- Flux Creative: 27 units due in 13 days (pretax budget cap $1,462,227)
- Ivory Labs: 19 units due in 13 days (pretax budget cap $1,022,866)
- Riverdale Initiative: 21 units due in 13 days (pretax budget cap $1,078,496)

On-hand finished stock covers 194 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.2% at selling price.

## Background & Policy

* Cover every customer order while using as little shared workcenter capacity as practical. If multiple feasible plans use the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.2% at selling price.
* Use the finished stock on hand where it helps reduce demand on shared workcenters.
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
* Review Internal Notes/comments on stock, customers, vendors, and workcenters before you confirm entries in the ERP.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
