**Priya Shah · Supply & Procurement · Teams**

All orders below for Centrifugal Compressor 200HP need confirmed supply coverage and scheduling.

- Garnet Fabricators: 18 units due in 8 days (pretax budget cap $965,790)
- Terra Studios South: 24 units due in 8 days (pretax budget cap $1,278,222)
- Ledger Research: 18 units due in 8 days (pretax budget cap $928,059)
- Mosaic Pictures: 23 units due in 8 days (pretax budget cap $1,210,970)
- Millbrook Architects: 32 units due in 8 days (pretax budget cap $1,749,605)
- Sentinel Creative: 18 units due in 8 days (pretax budget cap $947,964)
- Monarch Atelier: 26 units due in 9 days (pretax budget cap $1,388,727)
- Aether Chambers: 25 units due in 10 days (pretax budget cap $1,370,281)
- Arrow Practice: 21 units due in 10 days (pretax budget cap $1,139,991)
- Haven Innovations: 20 units due in 10 days (pretax budget cap $1,025,181)
- Ridge Collective East: 23 units due in 10 days (pretax budget cap $1,207,748)
- Sierra Studios: 21 units due in 11 days (pretax budget cap $1,142,898)
- Evergreen Academy: 21 units due in 11 days (pretax budget cap $1,077,642)
- Bayshore Society: 25 units due in 11 days (pretax budget cap $1,390,172)
- Jade Holdings: 32 units due in 12 days (pretax budget cap $1,651,398)
- Cedar Exchange: 20 units due in 12 days (pretax budget cap $1,077,100)
- Eclipse Partners: 28 units due in 12 days (pretax budget cap $1,464,339)
- Globe Boutique: 23 units due in 12 days (pretax budget cap $1,207,555)
- Oakmont Brands: 22 units due in 12 days (pretax budget cap $1,145,528)
- Nexus Bazaar: 24 units due in 12 days (pretax budget cap $1,257,477)
- Spire Collective: 32 units due in 13 days (pretax budget cap $1,780,560)
- Arc Robotics: 32 units due in 13 days (pretax budget cap $1,778,286)

On-hand finished stock covers 212 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.7% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.7% at selling price.
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
