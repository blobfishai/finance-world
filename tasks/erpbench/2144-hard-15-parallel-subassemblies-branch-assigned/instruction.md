**Priya Shah · Supply & Procurement · Teams**

All orders below for Portable Power Station 3kWh need confirmed supply coverage and scheduling.

- Marble Observatory: 19 units due in 8 days (pretax budget cap $58,130)
- Forge Dynamics: 18 units due in 8 days (pretax budget cap $57,406)
- Aurora Collective East: 18 units due in 8 days (pretax budget cap $54,431)
- Ember Arena: 18 units due in 8 days (pretax budget cap $55,690)
- Crown Works: 21 units due in 8 days (pretax budget cap $65,303)
- Hartland Theater: 18 units due in 8 days (pretax budget cap $55,782)
- Haven Productions: 19 units due in 8 days (pretax budget cap $57,965)
- Monarch Reserve: 20 units due in 8 days (pretax budget cap $60,246)
- Metro Atelier: 24 units due in 9 days (pretax budget cap $76,407)
- Meridian Publishing: 18 units due in 9 days (pretax budget cap $52,527)
- Summit Advisory: 21 units due in 9 days (pretax budget cap $63,638)
- Oxide Studios North: 18 units due in 9 days (pretax budget cap $55,107)
- Oakmont Workshop: 23 units due in 10 days (pretax budget cap $67,454)
- Flint Solutions Group: 20 units due in 10 days (pretax budget cap $64,080)
- Helix Studios West: 27 units due in 10 days (pretax budget cap $79,359)
- Sterling Pavilion: 19 units due in 11 days (pretax budget cap $56,080)
- Quantum Architects: 18 units due in 11 days (pretax budget cap $54,496)
- Cardinal Trading Co: 18 units due in 11 days (pretax budget cap $53,629)
- Aegis Society: 22 units due in 11 days (pretax budget cap $68,840)
- Ironside Alliance: 20 units due in 12 days (pretax budget cap $63,101)
- Northbridge Manufactory: 21 units due in 12 days (pretax budget cap $64,478)
- Crest Sciences: 18 units due in 13 days (pretax budget cap $54,838)
- Baltic Consortium: 23 units due in 13 days (pretax budget cap $67,443)
- Trident Technologies: 21 units due in 13 days (pretax budget cap $62,643)
- Axis Partners: 19 units due in 13 days (pretax budget cap $57,175)
- Scion Museum: 19 units due in 13 days (pretax budget cap $56,782)

On-hand finished stock covers 208 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.9% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* The combined units covered through new purchasing or manufacturing must clear at least 26.9% portfolio-level new-spend margin at selling price.
* Use available finished stock where it helps preserve shared workcenter capacity.
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
