**Priya Shah · Supply & Procurement · Teams**

Ensure all these Low-Pressure Blower Package 25HP customer orders are supplied on schedule:

- Lakewood Trust: 20 units due in 8 days (pretax budget cap $213,657)
- Iron Academy: 18 units due in 8 days (pretax budget cap $196,739)
- Spire Ventures: 24 units due in 8 days (pretax budget cap $272,203)
- Matrix Chambers: 20 units due in 8 days (pretax budget cap $221,173)
- Horizon Society: 19 units due in 8 days (pretax budget cap $205,889)
- Monarch Group: 19 units due in 8 days (pretax budget cap $212,538)
- Sterling Pavilion: 26 units due in 8 days (pretax budget cap $274,832)
- Trellis Atelier: 18 units due in 8 days (pretax budget cap $190,625)
- Beacon Cooperative: 25 units due in 9 days (pretax budget cap $284,077)
- Westfield Research: 26 units due in 9 days (pretax budget cap $278,213)
- Aether Theater: 20 units due in 9 days (pretax budget cap $223,962)
- Velocity Analytics: 18 units due in 9 days (pretax budget cap $196,585)
- Chrome Practice: 19 units due in 10 days (pretax budget cap $205,091)
- Dune Studios South: 18 units due in 10 days (pretax budget cap $187,286)
- Thornton Designs: 20 units due in 10 days (pretax budget cap $217,711)
- Fairview Observatory: 31 units due in 10 days (pretax budget cap $324,307)
- Crestview Media: 18 units due in 11 days (pretax budget cap $201,422)
- Lumen Collective: 18 units due in 11 days (pretax budget cap $189,907)
- Canton Greenhouse: 18 units due in 11 days (pretax budget cap $192,633)
- Helix Arena: 24 units due in 11 days (pretax budget cap $250,131)
- Bridgeway Clinics: 18 units due in 11 days (pretax budget cap $187,714)
- Element Institute: 22 units due in 12 days (pretax budget cap $236,789)
- Blaze Brands: 19 units due in 12 days (pretax budget cap $216,750)
- Polar Publishing: 18 units due in 12 days (pretax budget cap $203,353)
- Noble Trading Co: 23 units due in 12 days (pretax budget cap $254,909)
- Evergreen Studios: 18 units due in 13 days (pretax budget cap $191,015)
- Circuit Collective East: 30 units due in 13 days (pretax budget cap $323,048)
- Baltic Consortium: 23 units due in 13 days (pretax budget cap $252,164)
- Hartland Reserve: 19 units due in 13 days (pretax budget cap $215,524)

On-hand finished stock covers 244 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.8% at selling price.

## Background & Policy

* Get every customer order covered while keeping as much shared workcenter capacity open as possible. Keep new purchasing and manufacturing spend as low as possible when workcenter-capacity use ties.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 25.8% new-spend margin at selling price.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
