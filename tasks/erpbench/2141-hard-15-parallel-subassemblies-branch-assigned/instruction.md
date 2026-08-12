**Priya Shah · Supply & Procurement · Teams**

Ensure all these Portable Power Station 3kWh customer orders are supplied on schedule:

- Solace Collective: 19 units due in 8 days (pretax budget cap $55,306)
- Stonewall Research: 22 units due in 8 days (pretax budget cap $67,564)
- Canton Trust: 22 units due in 8 days (pretax budget cap $65,613)
- Clearwater Productions: 18 units due in 8 days (pretax budget cap $51,374)
- Cobalt Innovations: 19 units due in 8 days (pretax budget cap $56,217)
- Polar Cooperative: 20 units due in 8 days (pretax budget cap $61,053)
- Marble Interactive: 32 units due in 9 days (pretax budget cap $95,218)
- Sapphire Boutique: 19 units due in 9 days (pretax budget cap $56,037)
- Lance Consortium: 18 units due in 9 days (pretax budget cap $51,002)
- Noble Initiative: 18 units due in 9 days (pretax budget cap $50,942)
- Crown Pictures: 18 units due in 9 days (pretax budget cap $53,056)
- Lakewood Refinery: 19 units due in 9 days (pretax budget cap $58,253)
- Haven Studios North: 25 units due in 9 days (pretax budget cap $76,512)
- Bridgeway Chambers: 20 units due in 10 days (pretax budget cap $61,820)
- Cardinal Dynamics: 32 units due in 10 days (pretax budget cap $98,260)
- Oakmont Foundry: 21 units due in 11 days (pretax budget cap $59,760)
- Catalyst Bureau: 25 units due in 11 days (pretax budget cap $71,903)
- Alpine Theater: 18 units due in 11 days (pretax budget cap $53,484)
- Lattice Technologies: 19 units due in 11 days (pretax budget cap $53,913)
- Horizon Publishing: 22 units due in 11 days (pretax budget cap $66,084)
- Globe Conservatory: 19 units due in 11 days (pretax budget cap $58,412)
- Ironwood Forum: 31 units due in 12 days (pretax budget cap $96,027)
- Brookfield Robotics: 23 units due in 12 days (pretax budget cap $68,639)
- Ridgeline Sciences: 19 units due in 12 days (pretax budget cap $58,583)
- Blaze Alliance: 25 units due in 13 days (pretax budget cap $73,118)
- Meridian Atelier: 24 units due in 13 days (pretax budget cap $69,836)
- Compass Institute: 19 units due in 13 days (pretax budget cap $58,252)
- Steel Outfitters: 32 units due in 13 days (pretax budget cap $95,959)
- Trellis Workshop: 20 units due in 13 days (pretax budget cap $59,420)

Current finished-goods stock is 256 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.2% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.2% new-spend margin at selling price.
* Available finished stock can be used where it helps keep shared workcenter capacity open.
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
