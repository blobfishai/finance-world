**Priya Shah · Supply & Procurement · Teams**

All orders below for Clean Agent FM-200 System need confirmed supply coverage and scheduling.

- Mosaic Publishing: 32 units due in 8 days (pretax budget cap $442,559)
- Horizon Workshop: 22 units due in 8 days (pretax budget cap $313,678)
- Quartz Labs: 21 units due in 8 days (pretax budget cap $283,423)
- Arc Boutique: 18 units due in 9 days (pretax budget cap $256,855)
- Quantum Advisory: 18 units due in 9 days (pretax budget cap $244,505)
- Pivot Enterprises: 26 units due in 9 days (pretax budget cap $376,468)
- Summit Observatory: 19 units due in 9 days (pretax budget cap $276,600)
- Raven Robotics: 32 units due in 9 days (pretax budget cap $459,964)
- Jade Studios: 23 units due in 9 days (pretax budget cap $319,751)
- Metro Partners: 19 units due in 10 days (pretax budget cap $254,930)
- Circuit Designs: 18 units due in 10 days (pretax budget cap $255,751)
- Oxide Studios West: 27 units due in 10 days (pretax budget cap $392,272)
- Slate Architects: 20 units due in 10 days (pretax budget cap $286,497)
- Zenith Atelier: 18 units due in 10 days (pretax budget cap $263,586)
- Compass Consortium: 22 units due in 10 days (pretax budget cap $303,791)
- Conduit Institute: 27 units due in 11 days (pretax budget cap $381,551)
- Catalyst Interactive: 19 units due in 11 days (pretax budget cap $271,118)
- Solace Lyceum: 30 units due in 12 days (pretax budget cap $429,202)
- Ridgeline Office: 19 units due in 12 days (pretax budget cap $257,907)
- Clearwater Chambers: 19 units due in 13 days (pretax budget cap $269,034)
- Thornton Pictures: 23 units due in 13 days (pretax budget cap $332,506)
- Chrome Gallery: 32 units due in 13 days (pretax budget cap $453,479)
- Lumen Academy: 32 units due in 13 days (pretax budget cap $459,477)
- Haven Cooperative: 32 units due in 13 days (pretax budget cap $439,389)
- Lance Theater: 32 units due in 13 days (pretax budget cap $464,132)

We have 240 finished units on hand. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.1% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 24.1% portfolio-level new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
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
