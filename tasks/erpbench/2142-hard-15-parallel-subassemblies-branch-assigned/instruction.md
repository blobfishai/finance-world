**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Portable Power Station 3kWh require confirmed supply to proceed with fulfillment:

- Atlas Studios: 19 units due in 8 days (pretax budget cap $56,767)
- Terra Productions: 18 units due in 8 days (pretax budget cap $53,395)
- Cedar Studios North: 18 units due in 9 days (pretax budget cap $53,500)
- Polar Supply Co: 18 units due in 9 days (pretax budget cap $53,297)
- Axis Interactive: 19 units due in 10 days (pretax budget cap $55,700)
- Thornton Trading Co: 27 units due in 10 days (pretax budget cap $78,727)
- Nimbus Forum: 20 units due in 11 days (pretax budget cap $57,013)
- Bridgeway Foundry: 18 units due in 11 days (pretax budget cap $53,317)
- Prism Institute: 21 units due in 11 days (pretax budget cap $63,449)
- Iron Creative: 20 units due in 11 days (pretax budget cap $61,681)
- Flint Analytics: 20 units due in 12 days (pretax budget cap $58,651)
- Jade Partners: 19 units due in 12 days (pretax budget cap $56,266)
- Blaze Conservatory: 18 units due in 12 days (pretax budget cap $54,888)
- Canton Studios West: 21 units due in 12 days (pretax budget cap $60,874)
- Evergreen Boutique: 20 units due in 12 days (pretax budget cap $59,800)
- Raven Chambers: 18 units due in 12 days (pretax budget cap $54,290)
- Stratos Consortium: 20 units due in 12 days (pretax budget cap $61,483)
- Comet Holdings: 22 units due in 12 days (pretax budget cap $66,624)
- Sierra Collective East: 18 units due in 12 days (pretax budget cap $52,452)
- Globe Agency: 26 units due in 13 days (pretax budget cap $75,758)

We have 160 finished units on hand. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.8% at selling price.

## Background & Policy

* Cover every customer order while using as little shared workcenter capacity as practical. If multiple feasible plans use the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 25.8% new-spend margin at selling price.
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
