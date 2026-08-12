**Priya Shah · Supply & Procurement · Teams**

Plan fulfillment for these outstanding Booster Compressor 500PSI orders to ensure timely deliveries:

- Flint Sciences: 18 units due in 8 days (pretax budget cap $575,389)
- Spectra Ventures: 18 units due in 8 days (pretax budget cap $588,134)
- Cedar Studios West: 19 units due in 8 days (pretax budget cap $602,430)
- Ironside Workspaces: 18 units due in 8 days (pretax budget cap $581,334)
- Silverline Fabricators: 19 units due in 8 days (pretax budget cap $604,500)
- Aether Interactive: 19 units due in 8 days (pretax budget cap $578,553)
- Pivot Brands: 18 units due in 8 days (pretax budget cap $546,997)
- Fairview Office: 19 units due in 9 days (pretax budget cap $617,774)
- Clearwater Archive: 20 units due in 10 days (pretax budget cap $638,727)
- Apex Advisory: 21 units due in 11 days (pretax budget cap $652,258)
- Ledger Architects: 21 units due in 11 days (pretax budget cap $679,285)
- Prism Manufactory: 18 units due in 11 days (pretax budget cap $549,800)
- Axis Dynamics: 19 units due in 11 days (pretax budget cap $572,211)
- Cosmo Media: 18 units due in 12 days (pretax budget cap $550,657)
- Compass Refinery: 18 units due in 12 days (pretax budget cap $559,515)
- Borough Collective: 18 units due in 12 days (pretax budget cap $549,218)
- Baltic Bureau: 20 units due in 13 days (pretax budget cap $643,971)
- Vertex Conservatory: 20 units due in 13 days (pretax budget cap $646,757)
- Metro Studios East: 21 units due in 13 days (pretax budget cap $654,644)
- Zenith Workshop: 18 units due in 13 days (pretax budget cap $547,919)
- Sapphire Lyceum: 19 units due in 13 days (pretax budget cap $576,705)

We have 160 finished units on hand. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* The combined units covered through new purchasing or manufacturing must clear at least 28% portfolio-level new-spend margin at selling price.
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
