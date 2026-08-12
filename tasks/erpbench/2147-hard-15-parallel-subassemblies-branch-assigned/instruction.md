**Priya Shah · Supply & Procurement · Teams**

Prepare a fulfillment strategy for all listed LFP Energy Storage Module 51.2V orders to meet due dates and avoid shortages.

- Metro Greenhouse: 19 units due in 8 days (pretax budget cap $103,396)
- Velocity Supply Co: 18 units due in 8 days (pretax budget cap $96,004)
- Cipher Pictures: 18 units due in 8 days (pretax budget cap $94,282)
- Mosaic Collective East: 27 units due in 9 days (pretax budget cap $152,485)
- Flux Creative: 32 units due in 9 days (pretax budget cap $170,208)
- Ember Brands: 28 units due in 9 days (pretax budget cap $153,141)
- Grove Collective: 18 units due in 9 days (pretax budget cap $96,124)
- Evergreen Lyceum: 30 units due in 9 days (pretax budget cap $165,761)
- Ridgeline Solutions Group: 28 units due in 9 days (pretax budget cap $146,640)
- Quartz Studios: 19 units due in 9 days (pretax budget cap $103,705)
- Aurora Trading Co: 20 units due in 10 days (pretax budget cap $113,434)
- Raven Studios East: 18 units due in 10 days (pretax budget cap $101,750)
- Horizon Agency: 20 units due in 10 days (pretax budget cap $103,718)
- Ridge Forum: 21 units due in 11 days (pretax budget cap $111,977)
- Globe Reserve: 26 units due in 11 days (pretax budget cap $136,052)
- Aether Interactive: 32 units due in 11 days (pretax budget cap $168,986)
- Atlas Office: 28 units due in 11 days (pretax budget cap $151,150)
- Matrix Media: 23 units due in 11 days (pretax budget cap $128,934)
- Stonewall Dynamics: 18 units due in 11 days (pretax budget cap $94,525)
- Citadel Group: 32 units due in 11 days (pretax budget cap $181,044)
- Lumen Manufactory: 23 units due in 12 days (pretax budget cap $126,189)
- Gateway Conservatory: 20 units due in 12 days (pretax budget cap $107,844)
- Comet Fabricators: 25 units due in 12 days (pretax budget cap $139,441)
- Steel Analytics: 32 units due in 12 days (pretax budget cap $178,581)
- Beacon Outfitters: 20 units due in 13 days (pretax budget cap $104,708)
- Indigo Holdings: 20 units due in 13 days (pretax budget cap $103,868)
- Monarch Advisory: 32 units due in 13 days (pretax budget cap $178,229)
- Pinnacle Ventures: 32 units due in 13 days (pretax budget cap $181,485)
- Apex Pavilion: 32 units due in 13 days (pretax budget cap $170,611)
- Oxide Museum: 32 units due in 13 days (pretax budget cap $175,796)
- Catalyst Guild: 32 units due in 13 days (pretax budget cap $168,880)

We have 310 finished units on hand. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.4% at selling price.

## Background & Policy

* Get every customer order covered while keeping as much shared workcenter capacity open as possible. Keep new purchasing and manufacturing spend as low as possible when workcenter-capacity use ties.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 27.4% new-spend margin at selling price.
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
