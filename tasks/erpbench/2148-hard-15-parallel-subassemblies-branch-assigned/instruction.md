**Priya Shah · Supply & Procurement · Teams**

Each customer order below requires a fulfillment-ready supply solution before its delivery due date:

- Canton Museum: 30 units due in 8 days (pretax budget cap $395,037)
- Oakmont Pictures: 23 units due in 8 days (pretax budget cap $312,870)
- Baseline Gallery: 27 units due in 8 days (pretax budget cap $377,120)
- Osprey Studios North: 19 units due in 8 days (pretax budget cap $262,928)
- Monarch Outfitters: 24 units due in 8 days (pretax budget cap $330,133)
- Compass Archive: 27 units due in 9 days (pretax budget cap $364,355)
- Comet Studios South: 21 units due in 9 days (pretax budget cap $293,724)
- Alpine Sciences: 21 units due in 9 days (pretax budget cap $281,326)
- Globe Designs: 22 units due in 9 days (pretax budget cap $303,334)
- Iron Bureau: 32 units due in 9 days (pretax budget cap $453,411)
- Westfield Creative: 29 units due in 9 days (pretax budget cap $385,418)
- Indigo Robotics: 23 units due in 10 days (pretax budget cap $313,823)
- Lattice Alliance: 18 units due in 10 days (pretax budget cap $255,613)
- Lance Office: 29 units due in 10 days (pretax budget cap $403,269)
- Zenith Boutique: 29 units due in 11 days (pretax budget cap $407,317)
- Oxide Cooperative: 21 units due in 11 days (pretax budget cap $300,767)
- Vantage Studios West: 30 units due in 11 days (pretax budget cap $401,257)
- Eclipse Refinery: 32 units due in 11 days (pretax budget cap $444,153)
- Northbridge Agency: 20 units due in 11 days (pretax budget cap $279,795)
- Spark Analytics: 23 units due in 12 days (pretax budget cap $312,970)
- Flint Ventures: 22 units due in 12 days (pretax budget cap $295,394)
- Nimbus Theater: 27 units due in 13 days (pretax budget cap $365,331)
- Chrome Studios East: 26 units due in 13 days (pretax budget cap $364,943)
- Lumen Collective East: 31 units due in 13 days (pretax budget cap $437,022)
- Copper Publishing: 32 units due in 13 days (pretax budget cap $438,060)
- Flux Atelier: 32 units due in 13 days (pretax budget cap $437,638)
- Alloy Practice: 32 units due in 13 days (pretax budget cap $440,006)

We have 281 finished units on hand. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.6% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* The combined units covered through new purchasing or manufacturing must clear at least 26.6% portfolio-level new-spend margin at selling price.
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

Work in the `odoo` ERP and commit the plan there.
