**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Solar Storage Battery Wall-Mount require confirmed supply to proceed with fulfillment:

- Globe Media: 18 units due in 8 days (pretax budget cap $84,262)
- Baseline Bureau: 29 units due in 8 days (pretax budget cap $128,511)
- Keystone Trading Co: 19 units due in 8 days (pretax budget cap $90,783)
- Blaze Society: 27 units due in 9 days (pretax budget cap $128,077)
- Bridgeway Reserve: 21 units due in 9 days (pretax budget cap $99,938)
- Quantum Atelier: 25 units due in 9 days (pretax budget cap $111,546)
- Terra Systems: 32 units due in 10 days (pretax budget cap $145,536)
- Ivory Forum: 24 units due in 10 days (pretax budget cap $114,766)
- Polar Foundry: 18 units due in 10 days (pretax budget cap $86,070)
- Mosaic Robotics: 22 units due in 10 days (pretax budget cap $97,604)
- Pinnacle Guild: 22 units due in 10 days (pretax budget cap $105,497)
- Trellis Institute: 22 units due in 10 days (pretax budget cap $101,082)
- Copper Technologies: 19 units due in 11 days (pretax budget cap $86,294)
- Horizon Studios South: 29 units due in 11 days (pretax budget cap $130,871)
- Slate Manufactory: 25 units due in 11 days (pretax budget cap $113,789)
- Indigo Studios East: 20 units due in 11 days (pretax budget cap $94,017)
- Stonewall Conservatory: 19 units due in 11 days (pretax budget cap $85,194)
- Oakmont Museum: 18 units due in 11 days (pretax budget cap $78,678)
- Westfield Innovations: 19 units due in 11 days (pretax budget cap $89,195)
- Axis Group: 28 units due in 12 days (pretax budget cap $128,546)
- Skyline Alliance: 32 units due in 12 days (pretax budget cap $143,165)
- Vertex Architects: 32 units due in 12 days (pretax budget cap $144,488)
- Marble Greenhouse: 30 units due in 12 days (pretax budget cap $139,936)
- Lumen Archive: 32 units due in 12 days (pretax budget cap $152,015)
- Cosmo Designs: 32 units due in 12 days (pretax budget cap $140,371)
- Dune Hub: 32 units due in 12 days (pretax budget cap $144,744)
- Pivot Interactive: 32 units due in 12 days (pretax budget cap $142,630)
- Noble Dynamics: 32 units due in 13 days (pretax budget cap $153,425)
- Sentinel Analytics: 32 units due in 13 days (pretax budget cap $140,958)
- Gateway Exchange: 32 units due in 13 days (pretax budget cap $150,107)
- Echo Advisory: 32 units due in 13 days (pretax budget cap $140,604)

Current finished-goods stock is 323 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.3% at selling price.

## Background & Policy

* Get every customer order covered while keeping as much shared workcenter capacity open as possible. Keep new purchasing and manufacturing spend as low as possible when workcenter-capacity use ties.
* The combined units covered through new purchasing or manufacturing must clear at least 26.3% portfolio-level new-spend margin at selling price.
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

Work in the `odoo` ERP and commit the plan there.
