**Priya Shah · Supply & Procurement · Teams**

All orders below for LFP Energy Storage Module 51.2V need confirmed supply coverage and scheduling.

- Ashford Ventures: 18 units due in 8 days (pretax budget cap $105,479)
- Spark Architects: 18 units due in 8 days (pretax budget cap $106,836)
- Cipher Partners: 20 units due in 8 days (pretax budget cap $116,691)
- Spectra Agency: 19 units due in 8 days (pretax budget cap $104,471)
- Nexus Pictures: 21 units due in 8 days (pretax budget cap $117,741)
- Arbor Group: 19 units due in 9 days (pretax budget cap $107,214)
- Monarch Designs: 18 units due in 9 days (pretax budget cap $100,637)
- Meridian Exchange: 21 units due in 9 days (pretax budget cap $123,501)
- Summit Advisory: 18 units due in 9 days (pretax budget cap $106,895)
- Raven Workspaces: 19 units due in 10 days (pretax budget cap $113,369)
- Metro Creative: 18 units due in 10 days (pretax budget cap $105,245)
- Flux Refinery: 20 units due in 10 days (pretax budget cap $118,815)
- Zenith Analytics: 19 units due in 10 days (pretax budget cap $106,533)
- Axis Collective East: 18 units due in 10 days (pretax budget cap $106,262)
- Sterling Solutions Group: 22 units due in 10 days (pretax budget cap $128,995)
- Haven Workshop: 32 units due in 11 days (pretax budget cap $177,998)
- Alpine Hub: 18 units due in 11 days (pretax budget cap $101,263)
- Anvil Clinics: 19 units due in 11 days (pretax budget cap $110,223)
- Dune Productions: 18 units due in 11 days (pretax budget cap $101,580)
- Echo Institute: 21 units due in 12 days (pretax budget cap $121,275)
- Orbital Society: 25 units due in 12 days (pretax budget cap $141,525)
- Sapphire Enterprises: 18 units due in 12 days (pretax budget cap $105,679)
- Matrix Media: 18 units due in 13 days (pretax budget cap $104,802)
- Stratos Academy: 23 units due in 13 days (pretax budget cap $135,124)

Current finished-goods stock is 192 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.1% at selling price.

## Background & Policy

* Cover every customer order while using as little shared workcenter capacity as practical. If multiple feasible plans use the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 27.1% new-spend margin at selling price.
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
