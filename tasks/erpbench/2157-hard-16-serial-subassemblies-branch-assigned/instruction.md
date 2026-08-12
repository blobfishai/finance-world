**Priya Shah · Supply & Procurement · Teams**

Supply plans must be created to fulfill each outstanding Reciprocating Piston Compressor 15HP customer order listed.

- Vantage Works: 18 units due in 8 days (pretax budget cap $131,698)
- Sierra Architects: 27 units due in 8 days (pretax budget cap $182,352)
- Peak Analytics: 22 units due in 8 days (pretax budget cap $157,675)
- Lumen Conservatory: 18 units due in 8 days (pretax budget cap $125,958)
- Quantum Collective East: 18 units due in 8 days (pretax budget cap $128,110)
- Silverline Ventures: 18 units due in 8 days (pretax budget cap $132,663)
- Westfield Bureau: 20 units due in 9 days (pretax budget cap $141,679)
- Meridian Studios North: 19 units due in 9 days (pretax budget cap $129,188)
- Coral Fabricators: 20 units due in 9 days (pretax budget cap $134,876)
- Arrow Studios West: 20 units due in 9 days (pretax budget cap $147,005)
- Ivory Pictures: 22 units due in 9 days (pretax budget cap $160,499)
- Fairview Arena: 18 units due in 9 days (pretax budget cap $126,928)
- Aurora Guild: 19 units due in 10 days (pretax budget cap $134,529)
- Gateway Designs: 20 units due in 11 days (pretax budget cap $142,754)
- Keystone Solutions Group: 18 units due in 11 days (pretax budget cap $129,309)
- Opal Publishing: 26 units due in 11 days (pretax budget cap $191,976)
- Scion Innovations: 21 units due in 11 days (pretax budget cap $148,495)
- Flint Advisory: 18 units due in 12 days (pretax budget cap $129,138)
- Element Practice: 21 units due in 12 days (pretax budget cap $151,956)
- Marble Initiative: 29 units due in 12 days (pretax budget cap $204,211)
- Drift Systems: 24 units due in 12 days (pretax budget cap $170,977)
- Indigo Studios East: 24 units due in 13 days (pretax budget cap $164,950)
- Pinnacle Holdings: 20 units due in 13 days (pretax budget cap $143,416)
- Grove Cooperative: 24 units due in 13 days (pretax budget cap $163,977)

On-hand finished stock covers 202 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.6% at selling price.

## Background & Policy

* Get every customer order covered while keeping as much shared workcenter capacity open as possible. Keep new purchasing and manufacturing spend as low as possible when workcenter-capacity use ties.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.6% at selling price.
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
