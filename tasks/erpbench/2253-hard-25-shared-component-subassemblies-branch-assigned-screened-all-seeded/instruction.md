**Priya Shah · Supply & Procurement · Teams**

Handle the list of live Fire Alarm Control Panel FACP order demands.

- Lakewood Chambers: 18 units due in 8 days (pretax budget cap $82,792)
- Pivot Studios South: 19 units due in 8 days (pretax budget cap $84,783)
- Titan Outfitters: 18 units due in 8 days (pretax budget cap $81,356)
- Ridge Reserve: 20 units due in 8 days (pretax budget cap $91,898)
- Horizon Collective East: 27 units due in 8 days (pretax budget cap $119,431)
- Bronze Robotics: 32 units due in 8 days (pretax budget cap $145,608)
- Canton Engineering: 20 units due in 9 days (pretax budget cap $84,842)
- Ember Advisory: 22 units due in 9 days (pretax budget cap $95,809)
- Scion Sciences: 26 units due in 9 days (pretax budget cap $118,821)
- Marble Clinics: 18 units due in 9 days (pretax budget cap $78,374)
- Atlas Interactive: 21 units due in 10 days (pretax budget cap $92,825)
- Orbital Analytics: 32 units due in 10 days (pretax budget cap $143,440)
- Slate Institute: 24 units due in 10 days (pretax budget cap $104,605)
- Comet Conservatory: 23 units due in 10 days (pretax budget cap $106,115)
- Fairview Technologies: 25 units due in 10 days (pretax budget cap $108,167)
- Meridian Workshop: 22 units due in 11 days (pretax budget cap $97,970)
- Brookfield Academy: 26 units due in 11 days (pretax budget cap $110,491)
- Haven Studios West: 32 units due in 12 days (pretax budget cap $142,035)
- Noble Dynamics: 18 units due in 12 days (pretax budget cap $82,682)
- Riverdale Productions: 32 units due in 12 days (pretax budget cap $139,124)
- Sterling Archive: 30 units due in 12 days (pretax budget cap $129,436)
- Forge Partners: 32 units due in 13 days (pretax budget cap $144,020)
- Beacon Studios East: 24 units due in 13 days (pretax budget cap $104,163)
- Spire Publishing: 32 units due in 13 days (pretax budget cap $144,724)
- Trident Works: 32 units due in 13 days (pretax budget cap $145,120)

We have 250 finished units on hand. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.4% at selling price.

## Background & Policy

* These are the rules for customer order acceptance.
* Accepted orders must allow at least 13 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Arrange supply for eligible orders, ensuring the least new investment.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 24.4% new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Fulfillment constraints for accepted orders:
- After an order is accepted, treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- For each component supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
