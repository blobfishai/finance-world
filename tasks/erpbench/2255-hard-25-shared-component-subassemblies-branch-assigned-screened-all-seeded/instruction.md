**Priya Shah · Supply & Procurement · Teams**

Review the open order requests for Clean Agent FM-200 System.

- Aurora Guild: 21 units due in 8 days (pretax budget cap $278,825)
- Skyline Ventures: 22 units due in 8 days (pretax budget cap $305,783)
- Orbital Hub: 18 units due in 8 days (pretax budget cap $252,485)
- Grove Conservatory: 24 units due in 8 days (pretax budget cap $324,619)
- Globe Labs: 19 units due in 9 days (pretax budget cap $253,309)
- Pivot Media: 18 units due in 9 days (pretax budget cap $245,311)
- Ridge Bazaar: 23 units due in 9 days (pretax budget cap $326,282)
- Velocity Foundry: 19 units due in 9 days (pretax budget cap $261,687)
- Silverline Analytics: 30 units due in 9 days (pretax budget cap $431,097)
- Terra Studios West: 20 units due in 9 days (pretax budget cap $277,256)
- Lakewood Studios South: 25 units due in 9 days (pretax budget cap $354,441)
- Solace Chambers: 19 units due in 9 days (pretax budget cap $251,134)
- Sentinel Boutique: 26 units due in 9 days (pretax budget cap $373,514)
- Equinox Robotics: 20 units due in 10 days (pretax budget cap $275,464)
- Dune Systems: 21 units due in 10 days (pretax budget cap $286,112)
- Anvil Collective: 18 units due in 10 days (pretax budget cap $240,866)
- Aegis Forum: 21 units due in 10 days (pretax budget cap $300,943)
- Cipher Trading Co: 18 units due in 10 days (pretax budget cap $253,018)
- Nexus Refinery: 18 units due in 11 days (pretax budget cap $255,124)
- Mosaic Collective East: 20 units due in 11 days (pretax budget cap $267,369)
- Bayshore Brands: 20 units due in 11 days (pretax budget cap $281,179)
- Westfield Society: 19 units due in 11 days (pretax budget cap $270,915)
- Garnet Manufactory: 19 units due in 11 days (pretax budget cap $258,313)
- Noble Publishing: 21 units due in 12 days (pretax budget cap $300,078)
- Conduit Workspaces: 32 units due in 12 days (pretax budget cap $436,169)
- Spire Interactive: 21 units due in 12 days (pretax budget cap $293,118)
- Granite Trust: 21 units due in 12 days (pretax budget cap $279,910)
- Quantum Outfitters: 18 units due in 13 days (pretax budget cap $248,503)
- Keystone Architects: 19 units due in 13 days (pretax budget cap $252,666)
- Gateway Archive: 18 units due in 13 days (pretax budget cap $258,424)
- Trident Designs: 22 units due in 13 days (pretax budget cap $304,644)
- Arbor Studios East: 22 units due in 13 days (pretax budget cap $294,649)

We have 269 finished units on hand. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.1% at selling price.

## Background & Policy

* Our criteria for accepting incoming customer orders are as follows.
* Accepted orders must allow at least 11 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Deliver eligible orders but focus on reducing fresh procurement or manufacturing expenses.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.1% at selling price.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

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
