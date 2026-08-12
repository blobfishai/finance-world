**Priya Shah · Supply & Procurement · Teams**

The following Foam Deluge System Package customer orders are firm and must be supplied on schedule:

- Zenith Cooperative: 18 units due in 8 days (pretax budget cap $175,969)
- Conduit Studios North: 18 units due in 8 days (pretax budget cap $165,380)
- Bayshore Office: 18 units due in 8 days (pretax budget cap $172,571)
- Skyline Group: 32 units due in 8 days (pretax budget cap $296,374)
- Canton Conservatory: 23 units due in 8 days (pretax budget cap $206,026)
- Flint Media: 18 units due in 8 days (pretax budget cap $162,925)
- Orbital Pavilion: 32 units due in 9 days (pretax budget cap $300,552)
- Grove Workspaces: 18 units due in 9 days (pretax budget cap $166,463)
- Crestview Ventures: 22 units due in 10 days (pretax budget cap $196,328)
- Ledger Bureau: 18 units due in 10 days (pretax budget cap $176,275)
- Sterling Creative: 23 units due in 11 days (pretax budget cap $206,322)
- Ironwood Technologies: 20 units due in 11 days (pretax budget cap $193,330)
- Ridge Manufactory: 20 units due in 11 days (pretax budget cap $192,570)
- Echo Collective East: 20 units due in 11 days (pretax budget cap $188,568)
- Quantum Solutions Group: 25 units due in 11 days (pretax budget cap $236,923)
- Globe Publishing: 28 units due in 11 days (pretax budget cap $269,837)
- Oxide Architects: 22 units due in 12 days (pretax budget cap $205,473)
- Ember Fabricators: 26 units due in 12 days (pretax budget cap $243,660)
- Keystone Agency: 23 units due in 12 days (pretax budget cap $207,313)
- Opal Guild: 21 units due in 12 days (pretax budget cap $201,598)
- Matrix Theater: 20 units due in 12 days (pretax budget cap $189,311)
- Cardinal Exchange: 23 units due in 12 days (pretax budget cap $218,801)
- Summit Designs: 23 units due in 13 days (pretax budget cap $207,853)
- Mosaic Lyceum: 21 units due in 13 days (pretax budget cap $189,708)
- Clearwater Clinics: 25 units due in 13 days (pretax budget cap $234,250)
- Aegis Analytics: 32 units due in 13 days (pretax budget cap $298,511)
- Onyx Boutique: 32 units due in 13 days (pretax budget cap $311,419)

On-hand finished stock covers 249 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.8% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.8% at selling price.
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
