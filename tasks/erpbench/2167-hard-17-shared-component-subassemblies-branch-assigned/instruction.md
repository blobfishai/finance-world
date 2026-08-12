**Priya Shah · Supply & Procurement · Teams**

Ensure all these Wet Sprinkler System Package customer orders are supplied on schedule:

- Ironside Studios West: 19 units due in 8 days (pretax budget cap $104,124)
- Iron Clinics: 19 units due in 8 days (pretax budget cap $97,559)
- Axis Publishing: 19 units due in 8 days (pretax budget cap $101,132)
- Redstone Agency: 18 units due in 8 days (pretax budget cap $92,666)
- Polar Cooperative: 24 units due in 8 days (pretax budget cap $131,177)
- Slate Technologies: 18 units due in 8 days (pretax budget cap $92,869)
- Evergreen Studios South: 20 units due in 8 days (pretax budget cap $108,949)
- Ironwood Trading Co: 19 units due in 8 days (pretax budget cap $104,492)
- Compass Designs: 24 units due in 8 days (pretax budget cap $128,015)
- Arc Chambers: 19 units due in 9 days (pretax budget cap $105,335)
- Beacon Architects: 26 units due in 9 days (pretax budget cap $144,341)
- Circuit Alliance: 24 units due in 10 days (pretax budget cap $123,146)
- Ember Workspaces: 21 units due in 10 days (pretax budget cap $107,380)
- Mosaic Brands: 19 units due in 10 days (pretax budget cap $105,665)
- Ashford Initiative: 24 units due in 10 days (pretax budget cap $128,386)
- Stonewall Practice: 18 units due in 10 days (pretax budget cap $100,091)
- Spark Consortium: 20 units due in 11 days (pretax budget cap $108,080)
- Ledger Creative: 19 units due in 11 days (pretax budget cap $97,760)
- Orbital Office: 19 units due in 11 days (pretax budget cap $99,165)
- Spire Sciences: 18 units due in 11 days (pretax budget cap $94,255)
- Lumen Refinery: 18 units due in 11 days (pretax budget cap $97,669)
- Stratos Greenhouse: 18 units due in 11 days (pretax budget cap $92,923)
- Summit Boutique: 21 units due in 12 days (pretax budget cap $110,917)
- Gateway Gallery: 18 units due in 12 days (pretax budget cap $97,490)
- Quartz Reserve: 20 units due in 12 days (pretax budget cap $103,414)
- Citadel Systems: 19 units due in 13 days (pretax budget cap $103,191)
- Onyx Institute: 18 units due in 13 days (pretax budget cap $99,193)
- Solace Dynamics: 21 units due in 13 days (pretax budget cap $110,249)
- Opal Holdings: 22 units due in 13 days (pretax budget cap $115,421)
- Conduit Bazaar: 19 units due in 13 days (pretax budget cap $105,000)
- Granite Analytics: 19 units due in 13 days (pretax budget cap $103,541)

Current finished-goods stock is 248 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.1% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 25.1% portfolio-level new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
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
