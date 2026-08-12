**Priya Shah · Supply & Procurement · Teams**

Each customer order below requires a fulfillment-ready supply solution before its delivery due date:

- Garnet Guild: 32 units due in 8 days (pretax budget cap $132,393)
- Terra Workshop: 21 units due in 8 days (pretax budget cap $91,224)
- Titan Studios East: 18 units due in 8 days (pretax budget cap $73,335)
- Eclipse Arena: 22 units due in 8 days (pretax budget cap $93,124)
- Vantage Trust: 18 units due in 8 days (pretax budget cap $78,142)
- Sapphire Engineering: 19 units due in 8 days (pretax budget cap $78,343)
- Sterling Brands: 28 units due in 9 days (pretax budget cap $111,635)
- Opal Exchange: 20 units due in 9 days (pretax budget cap $86,024)
- Mosaic Partners: 18 units due in 9 days (pretax budget cap $77,949)
- Quartz Pavilion: 18 units due in 9 days (pretax budget cap $77,673)
- Northbridge Sciences: 21 units due in 10 days (pretax budget cap $86,710)
- Compass Initiative: 29 units due in 10 days (pretax budget cap $120,205)
- Brookfield Supply Co: 18 units due in 10 days (pretax budget cap $72,756)
- Onyx Advisory: 29 units due in 10 days (pretax budget cap $126,004)
- Spectra Workspaces: 19 units due in 11 days (pretax budget cap $80,170)
- Ashford Consortium: 21 units due in 11 days (pretax budget cap $84,629)
- Meridian Agency: 19 units due in 11 days (pretax budget cap $80,357)
- Helix Publishing: 21 units due in 11 days (pretax budget cap $89,157)
- Iron Research: 21 units due in 12 days (pretax budget cap $86,451)
- Blaze Collective East: 24 units due in 12 days (pretax budget cap $102,909)
- Cedar Creative: 18 units due in 12 days (pretax budget cap $76,823)
- Echo Interactive: 19 units due in 12 days (pretax budget cap $81,671)
- Nexus Innovations: 19 units due in 12 days (pretax budget cap $79,663)
- Borough Archive: 32 units due in 12 days (pretax budget cap $138,783)
- Gateway Greenhouse: 26 units due in 12 days (pretax budget cap $103,838)
- Nimbus Forum: 27 units due in 12 days (pretax budget cap $116,870)
- Baseline Conservatory: 21 units due in 12 days (pretax budget cap $88,888)
- Crest Theater: 22 units due in 13 days (pretax budget cap $96,020)
- Peak Productions: 29 units due in 13 days (pretax budget cap $116,357)
- Horizon Designs: 32 units due in 13 days (pretax budget cap $137,250)
- Ridge Group: 32 units due in 13 days (pretax budget cap $136,365)

Current finished-goods stock is 286 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.8% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 28.8% new-spend margin at selling price.
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

Work in the `odoo` ERP and commit the plan there.
