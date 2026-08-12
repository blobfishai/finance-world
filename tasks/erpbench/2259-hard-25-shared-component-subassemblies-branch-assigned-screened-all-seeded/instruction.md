**Priya Shah · Supply & Procurement · Teams**

Handle the open CO2 Total Flooding System order queue.

- Stratos Studios: 18 units due in 8 days (pretax budget cap $189,038)
- Granite Publishing: 19 units due in 8 days (pretax budget cap $199,663)
- Globe Works: 19 units due in 8 days (pretax budget cap $202,831)
- Slate Innovations: 21 units due in 8 days (pretax budget cap $232,472)
- Pacific Collective East: 19 units due in 8 days (pretax budget cap $196,667)
- Velocity Collective: 21 units due in 8 days (pretax budget cap $226,922)
- Haven Studios North: 32 units due in 9 days (pretax budget cap $361,196)
- Cedar Foundry: 20 units due in 9 days (pretax budget cap $212,082)
- Spectra Society: 25 units due in 9 days (pretax budget cap $268,610)
- Spire Atelier: 18 units due in 9 days (pretax budget cap $188,501)
- Marble Gallery: 32 units due in 10 days (pretax budget cap $331,006)
- Vantage Guild: 21 units due in 10 days (pretax budget cap $227,442)
- Sentinel Holdings: 21 units due in 10 days (pretax budget cap $226,963)
- Comet Pictures: 25 units due in 11 days (pretax budget cap $281,560)
- Lakewood Manufactory: 20 units due in 11 days (pretax budget cap $207,465)
- Baltic Studios West: 23 units due in 11 days (pretax budget cap $255,399)
- Solace Archive: 32 units due in 11 days (pretax budget cap $359,243)
- Arbor Group: 29 units due in 11 days (pretax budget cap $300,775)
- Alloy Bazaar: 32 units due in 12 days (pretax budget cap $351,708)
- Ridge Council: 32 units due in 13 days (pretax budget cap $333,337)
- Pivot Observatory: 32 units due in 13 days (pretax budget cap $353,440)
- Lattice Trading Co: 32 units due in 13 days (pretax budget cap $340,517)
- Conduit Bureau: 32 units due in 13 days (pretax budget cap $338,577)

On-hand finished stock covers 230 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29% at selling price.

## Background & Policy

* Customer order acceptance is based on the following criteria.
* Accepted orders must allow at least 9 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Arrange supply for eligible orders, ensuring the least new investment.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29% at selling price.
* Finance considers the existing stock as sunk cost.
* Some sales documents may already exist in draft; review existing documents before creating new ones.
* Cancel any already-drafted sales order that fails those acceptance rules.
* Customer budgets are pre-tax amounts.
* Link every accepted Sales Order to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* For subassembly or intermediate MOs, put the immediate parent MO reference(s) that the subassembly feeds (e.g. WH/MO/00020 or WH/MO/00020, WH/MO/00021) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> (Subassembly MO if needed) -> PO or SO -> PO for every incoming customer order you accept.
* You must sell this product at List Price.
* On every accepted Sales Order, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* If you choose to manufacture, you must procure the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Fulfillment constraints for accepted orders:
- After an order is accepted, treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- For each component supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
