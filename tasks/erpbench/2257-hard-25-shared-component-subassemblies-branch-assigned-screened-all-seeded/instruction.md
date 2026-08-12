**Priya Shah · Supply & Procurement · Teams**

Handle the open Fire Alarm Control Panel FACP order queue.

- Stonewall Trust: 18 units due in 8 days (pretax budget cap $78,021)
- Copper Reserve: 23 units due in 8 days (pretax budget cap $97,132)
- Spectra Practice: 24 units due in 8 days (pretax budget cap $98,717)
- Compass Forum: 19 units due in 8 days (pretax budget cap $80,288)
- Beacon Pavilion: 20 units due in 8 days (pretax budget cap $83,965)
- Chrome Advisory: 20 units due in 8 days (pretax budget cap $87,086)
- Vertex Initiative: 20 units due in 9 days (pretax budget cap $87,783)
- Keystone Sciences: 27 units due in 9 days (pretax budget cap $118,945)
- Terra Museum: 18 units due in 9 days (pretax budget cap $76,309)
- Atlas Trading Co: 23 units due in 9 days (pretax budget cap $95,156)
- Arrow Hub: 23 units due in 9 days (pretax budget cap $102,848)
- Blaze Atelier: 18 units due in 10 days (pretax budget cap $78,954)
- Peak Studios East: 18 units due in 10 days (pretax budget cap $79,516)
- Nexus Foundry: 18 units due in 10 days (pretax budget cap $76,644)
- Element Refinery: 19 units due in 11 days (pretax budget cap $85,025)
- Steel Agency: 22 units due in 11 days (pretax budget cap $91,118)
- Haven Creative: 25 units due in 11 days (pretax budget cap $106,723)
- Equinox Designs: 18 units due in 12 days (pretax budget cap $77,932)
- Oakmont Consortium: 22 units due in 12 days (pretax budget cap $97,932)
- Bayshore Studios West: 19 units due in 13 days (pretax budget cap $79,665)
- Westfield Gallery: 27 units due in 13 days (pretax budget cap $117,601)

On-hand finished stock covers 177 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.3% at selling price.

## Background & Policy

* The rules for which orders can be accepted are outlined below.
* Accepted orders must allow at least 9 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* After acceptance, cover each qualifying order while achieving the lowest possible new outlay.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 28.3% new-spend margin at selling price.
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
