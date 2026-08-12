**Priya Shah · Supply & Procurement · Teams**

Prepare a fulfillment strategy for all listed Wet Sprinkler System Package orders to meet due dates and avoid shortages.

- Skyline Chambers: 20 units due in 8 days (pretax budget cap $101,480)
- Trident Research: 18 units due in 8 days (pretax budget cap $95,420)
- Cobalt Refinery: 24 units due in 9 days (pretax budget cap $121,845)
- Thornton Studios South: 20 units due in 9 days (pretax budget cap $101,668)
- Sentinel Sciences: 26 units due in 9 days (pretax budget cap $143,636)
- Stratos Agency: 18 units due in 9 days (pretax budget cap $99,296)
- Granite Partners: 23 units due in 9 days (pretax budget cap $124,568)
- Apex Manufactory: 18 units due in 9 days (pretax budget cap $95,294)
- Scion Ventures: 18 units due in 9 days (pretax budget cap $96,926)
- Summit Enterprises: 21 units due in 10 days (pretax budget cap $113,876)
- Chrome Robotics: 20 units due in 10 days (pretax budget cap $104,527)
- Cascade Greenhouse: 32 units due in 11 days (pretax budget cap $173,474)
- Cardinal Observatory: 26 units due in 12 days (pretax budget cap $140,139)
- Copper Analytics: 32 units due in 12 days (pretax budget cap $175,425)
- Coral Lyceum: 19 units due in 12 days (pretax budget cap $105,408)
- Fairview Fabricators: 32 units due in 12 days (pretax budget cap $171,086)
- Titan Office: 30 units due in 12 days (pretax budget cap $164,994)
- Grove Interactive: 32 units due in 12 days (pretax budget cap $176,951)
- Comet Workspaces: 32 units due in 13 days (pretax budget cap $171,621)
- Helix Forum: 32 units due in 13 days (pretax budget cap $170,056)
- Ember Collective East: 32 units due in 13 days (pretax budget cap $175,122)

On-hand finished stock covers 210 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 25% portfolio-level new-spend margin at selling price.
* Accounting treats the existing stock as sunk cost.
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
