**Priya Shah · Supply & Procurement · Teams**

Prepare a fulfillment strategy for all listed Fire Alarm Control Panel FACP orders to meet due dates and avoid shortages.

- Crown Trust: 18 units due in 8 days (pretax budget cap $76,849)
- Bayshore Dynamics: 19 units due in 8 days (pretax budget cap $88,079)
- Summit Lyceum: 24 units due in 8 days (pretax budget cap $108,956)
- Aether Pavilion: 24 units due in 8 days (pretax budget cap $104,863)
- Equinox Society: 18 units due in 8 days (pretax budget cap $78,824)
- Sapphire Boutique: 18 units due in 9 days (pretax budget cap $80,144)
- Quartz Engineering: 23 units due in 9 days (pretax budget cap $100,283)
- Trident Labs: 21 units due in 9 days (pretax budget cap $95,134)
- Scion Supply Co: 18 units due in 9 days (pretax budget cap $77,786)
- Nimbus Solutions Group: 25 units due in 10 days (pretax budget cap $109,235)
- Crestview Forum: 24 units due in 10 days (pretax budget cap $104,160)
- Arbor Academy: 25 units due in 10 days (pretax budget cap $110,200)
- Chrome Analytics: 22 units due in 10 days (pretax budget cap $97,251)
- Atlas Agency: 21 units due in 10 days (pretax budget cap $89,989)
- Osprey Studios West: 30 units due in 10 days (pretax budget cap $134,870)
- Cipher Brands: 19 units due in 10 days (pretax budget cap $84,792)
- Grove Manufactory: 18 units due in 11 days (pretax budget cap $80,277)
- Compass Collective East: 21 units due in 11 days (pretax budget cap $94,971)
- Pacific Workshop: 18 units due in 12 days (pretax budget cap $79,169)
- Flint Observatory: 22 units due in 12 days (pretax budget cap $96,872)
- Comet Arena: 18 units due in 12 days (pretax budget cap $79,861)
- Eclipse Interactive: 22 units due in 12 days (pretax budget cap $94,032)
- Axis Bureau: 19 units due in 12 days (pretax budget cap $80,809)
- Borough Bazaar: 18 units due in 13 days (pretax budget cap $76,082)
- Gateway Technologies: 30 units due in 13 days (pretax budget cap $130,290)
- Ridge Workspaces: 18 units due in 13 days (pretax budget cap $81,936)
- Cobalt Research: 32 units due in 13 days (pretax budget cap $141,224)
- Catalyst Consortium: 32 units due in 13 days (pretax budget cap $140,917)
- Quantum Holdings: 32 units due in 13 days (pretax budget cap $143,212)
- Aurora Chambers: 32 units due in 13 days (pretax budget cap $144,242)
- Ridgeline Pictures: 32 units due in 13 days (pretax budget cap $136,291)

Current finished-goods stock is 286 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.4% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 28.4% portfolio-level new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
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

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
