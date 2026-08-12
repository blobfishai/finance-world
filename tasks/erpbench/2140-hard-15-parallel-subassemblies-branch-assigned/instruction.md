**Priya Shah · Supply & Procurement · Teams**

Ensure all these Modular Rack Battery System 20kWh customer orders are supplied on schedule:

- Polar Publishing: 32 units due in 8 days (pretax budget cap $566,837)
- Cosmo Chambers: 26 units due in 8 days (pretax budget cap $434,780)
- Lumen Collective: 20 units due in 8 days (pretax budget cap $346,856)
- Canton Holdings: 23 units due in 9 days (pretax budget cap $386,536)
- Lattice Museum: 31 units due in 9 days (pretax budget cap $511,919)
- Quartz Society: 18 units due in 9 days (pretax budget cap $320,176)
- Gateway Ventures: 19 units due in 10 days (pretax budget cap $311,043)
- Helix Systems: 18 units due in 10 days (pretax budget cap $321,366)
- Millbrook Advisory: 18 units due in 11 days (pretax budget cap $309,925)
- Arbor Collective East: 19 units due in 11 days (pretax budget cap $333,316)
- Element Council: 18 units due in 11 days (pretax budget cap $305,523)
- Keystone Agency: 22 units due in 11 days (pretax budget cap $369,676)
- Jade Enterprises: 32 units due in 11 days (pretax budget cap $539,956)
- Aurora Labs: 26 units due in 11 days (pretax budget cap $461,750)
- Riverdale Brands: 32 units due in 12 days (pretax budget cap $531,890)
- Trident Technologies: 32 units due in 12 days (pretax budget cap $551,665)
- Oxide Group: 32 units due in 12 days (pretax budget cap $540,368)
- Conduit Exchange: 32 units due in 13 days (pretax budget cap $558,154)
- Westfield Greenhouse: 32 units due in 13 days (pretax budget cap $531,516)
- Granite Office: 32 units due in 13 days (pretax budget cap $560,992)
- Copper Refinery: 32 units due in 13 days (pretax budget cap $565,810)

Current finished-goods stock is 219 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25% at selling price.

## Background & Policy

* Get every customer order covered while keeping as much shared workcenter capacity open as possible. Keep new purchasing and manufacturing spend as low as possible when workcenter-capacity use ties.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 25% new-spend margin at selling price.
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
