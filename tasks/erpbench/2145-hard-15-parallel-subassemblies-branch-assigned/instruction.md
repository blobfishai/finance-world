**Priya Shah · Supply & Procurement · Teams**

All orders below for LFP Energy Storage Module 51.2V need confirmed supply coverage and scheduling.

- Gateway Observatory: 18 units due in 8 days (pretax budget cap $103,611)
- Steel Museum: 32 units due in 8 days (pretax budget cap $172,954)
- Copper Supply Co: 18 units due in 8 days (pretax budget cap $98,182)
- Silverline Media: 18 units due in 8 days (pretax budget cap $102,105)
- Flux Holdings: 18 units due in 9 days (pretax budget cap $101,103)
- Cedar Productions: 27 units due in 9 days (pretax budget cap $143,942)
- Zenith Studios West: 21 units due in 9 days (pretax budget cap $111,552)
- Spectra Gallery: 27 units due in 9 days (pretax budget cap $147,319)
- Slate Conservatory: 23 units due in 9 days (pretax budget cap $125,616)
- Trident Partners: 24 units due in 9 days (pretax budget cap $133,849)
- Hartland Initiative: 20 units due in 9 days (pretax budget cap $109,104)
- Peak Refinery: 22 units due in 9 days (pretax budget cap $127,031)
- Ridgeline Fabricators: 25 units due in 10 days (pretax budget cap $134,453)
- Atlas Atelier: 26 units due in 10 days (pretax budget cap $140,283)
- Trellis Pavilion: 21 units due in 11 days (pretax budget cap $113,700)
- Eclipse Interactive: 18 units due in 11 days (pretax budget cap $100,853)
- Pacific Hub: 32 units due in 11 days (pretax budget cap $181,855)
- Forge Cooperative: 21 units due in 11 days (pretax budget cap $111,128)
- Pivot Sciences: 21 units due in 11 days (pretax budget cap $113,330)
- Vantage Society: 19 units due in 11 days (pretax budget cap $106,807)
- Ridge Advisory: 32 units due in 12 days (pretax budget cap $174,101)
- Aether Studios South: 18 units due in 12 days (pretax budget cap $98,771)
- Horizon Research: 25 units due in 12 days (pretax budget cap $132,456)
- Vertex Solutions Group: 20 units due in 13 days (pretax budget cap $111,540)
- Cardinal Innovations: 21 units due in 13 days (pretax budget cap $120,223)
- Granite Designs: 31 units due in 13 days (pretax budget cap $171,104)

On-hand finished stock covers 240 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* The combined units covered through new purchasing or manufacturing must clear at least 29% portfolio-level new-spend margin at selling price.
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
