**Priya Shah · Supply & Procurement · Teams**

Work through the current order queue for Fire Alarm Control Panel FACP.

- Northbridge Collective: 20 units due in 8 days (pretax budget cap $94,341)
- Baseline Supply Co: 18 units due in 8 days (pretax budget cap $79,634)
- Lakewood Gallery: 18 units due in 8 days (pretax budget cap $85,082)
- Atlas Exchange: 18 units due in 9 days (pretax budget cap $84,345)
- Aether Studios: 29 units due in 9 days (pretax budget cap $126,422)
- Coral Initiative: 19 units due in 9 days (pretax budget cap $84,105)
- Gateway Dynamics: 18 units due in 9 days (pretax budget cap $79,311)
- Conduit Partners: 26 units due in 9 days (pretax budget cap $113,691)
- Polar Productions: 21 units due in 10 days (pretax budget cap $91,106)
- Mosaic Consortium: 21 units due in 10 days (pretax budget cap $98,981)
- Granite Guild: 23 units due in 10 days (pretax budget cap $102,747)
- Comet Pavilion: 21 units due in 11 days (pretax budget cap $96,431)
- Crestview Studios South: 19 units due in 11 days (pretax budget cap $84,616)
- Skyline Foundry: 18 units due in 11 days (pretax budget cap $84,035)
- Ember Studios West: 22 units due in 11 days (pretax budget cap $100,858)
- Keystone Analytics: 25 units due in 11 days (pretax budget cap $117,218)
- Catalyst Enterprises: 21 units due in 12 days (pretax budget cap $99,221)
- Vertex Collective East: 32 units due in 12 days (pretax budget cap $148,263)
- Lance Brands: 20 units due in 12 days (pretax budget cap $88,068)
- Crest Systems: 18 units due in 12 days (pretax budget cap $78,260)
- Bronze Solutions Group: 18 units due in 12 days (pretax budget cap $83,526)
- Steel Conservatory: 30 units due in 12 days (pretax budget cap $136,057)
- Baltic Pictures: 18 units due in 13 days (pretax budget cap $85,182)
- Slate Atelier: 32 units due in 13 days (pretax budget cap $149,386)
- Garnet Holdings: 25 units due in 13 days (pretax budget cap $108,436)

Current finished-goods stock is 220 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.4% at selling price.

## Background & Policy

* Order acceptance must follow these rules.
* Accepted orders must allow at least 11 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For every accepted order, provide supply coverage with minimal new spend.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.4% new-spend margin at selling price.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Fulfillment constraints for accepted orders:
- After an order is accepted, treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- For each component supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
