**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Booster Compressor 500PSI require confirmed supply to proceed with fulfillment:

- Westfield Analytics: 18 units due in 8 days (pretax budget cap $572,100)
- Mosaic Fabricators: 18 units due in 8 days (pretax budget cap $537,839)
- Slate Research: 18 units due in 9 days (pretax budget cap $578,431)
- Cascade Architects: 18 units due in 9 days (pretax budget cap $545,222)
- Bayshore Bureau: 19 units due in 9 days (pretax budget cap $585,418)
- Conduit Enterprises: 18 units due in 9 days (pretax budget cap $573,033)
- Riverdale Bazaar: 24 units due in 10 days (pretax budget cap $748,484)
- Element Conservatory: 20 units due in 10 days (pretax budget cap $601,992)
- Borough Group: 20 units due in 10 days (pretax budget cap $609,610)
- Equinox Works: 21 units due in 10 days (pretax budget cap $635,789)
- Cipher Initiative: 22 units due in 10 days (pretax budget cap $696,872)
- Oakmont Publishing: 24 units due in 11 days (pretax budget cap $722,296)
- Ember Pavilion: 29 units due in 11 days (pretax budget cap $926,439)
- Ivory Forum: 26 units due in 11 days (pretax budget cap $821,251)
- Pivot Theater: 22 units due in 11 days (pretax budget cap $660,135)
- Sterling Arena: 32 units due in 11 days (pretax budget cap $1,019,054)
- Pacific Ventures: 30 units due in 12 days (pretax budget cap $906,626)
- Axis Pictures: 19 units due in 12 days (pretax budget cap $566,429)
- Polar Trust: 30 units due in 13 days (pretax budget cap $919,778)
- Vertex Media: 32 units due in 13 days (pretax budget cap $966,667)

On-hand finished stock covers 184 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.2% at selling price.

## Background & Policy

* Get every customer order covered while keeping as much shared workcenter capacity open as possible. Keep new purchasing and manufacturing spend as low as possible when workcenter-capacity use ties.
* The combined units covered through new purchasing or manufacturing must clear at least 25.2% portfolio-level new-spend margin at selling price.
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
