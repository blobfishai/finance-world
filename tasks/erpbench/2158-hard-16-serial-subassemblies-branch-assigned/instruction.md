**Priya Shah · Supply & Procurement · Teams**

Each customer order below requires a fulfillment-ready supply solution before its delivery due date:

- Cipher Supply Co: 20 units due in 8 days (pretax budget cap $560,115)
- Granite Agency: 18 units due in 8 days (pretax budget cap $516,494)
- Brookfield Guild: 20 units due in 8 days (pretax budget cap $590,590)
- Meridian Atelier: 22 units due in 8 days (pretax budget cap $661,603)
- Lance Group: 18 units due in 8 days (pretax budget cap $534,336)
- Circuit Dynamics: 32 units due in 8 days (pretax budget cap $933,053)
- Mosaic Forum: 20 units due in 8 days (pretax budget cap $566,176)
- Arc Architects: 18 units due in 8 days (pretax budget cap $547,476)
- Spire Interactive: 22 units due in 8 days (pretax budget cap $630,582)
- Stonewall Labs: 18 units due in 9 days (pretax budget cap $514,945)
- Copper Gallery: 19 units due in 9 days (pretax budget cap $539,862)
- Alloy Media: 19 units due in 10 days (pretax budget cap $572,970)
- Orbital Refinery: 23 units due in 10 days (pretax budget cap $689,243)
- Helix Collective East: 23 units due in 10 days (pretax budget cap $676,825)
- Alpine Lyceum: 20 units due in 10 days (pretax budget cap $570,415)
- Ironwood Theater: 20 units due in 10 days (pretax budget cap $572,695)
- Riverdale Sciences: 20 units due in 11 days (pretax budget cap $607,134)
- Borough Technologies: 20 units due in 11 days (pretax budget cap $554,153)
- Crest Archive: 18 units due in 11 days (pretax budget cap $541,343)
- Conduit Clinics: 18 units due in 12 days (pretax budget cap $544,326)
- Cobalt Trust: 32 units due in 12 days (pretax budget cap $953,254)
- Velocity Hub: 19 units due in 12 days (pretax budget cap $577,125)
- Evergreen Pavilion: 19 units due in 12 days (pretax budget cap $530,583)
- Prism Works: 21 units due in 13 days (pretax budget cap $601,413)
- Horizon Pictures: 25 units due in 13 days (pretax budget cap $706,617)
- Pinnacle Manufactory: 22 units due in 13 days (pretax budget cap $654,596)

On-hand finished stock covers 219 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.6% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.6% at selling price.
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

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
