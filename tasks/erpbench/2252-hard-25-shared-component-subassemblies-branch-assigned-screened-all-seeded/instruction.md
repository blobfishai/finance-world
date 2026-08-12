**Priya Shah · Supply & Procurement · Teams**

Address the current order backlog for Kitchen Hood Suppression Unit.

- Comet Enterprises: 32 units due in 8 days (pretax budget cap $109,906)
- Noble Atelier: 18 units due in 8 days (pretax budget cap $59,244)
- Cosmo Initiative: 22 units due in 8 days (pretax budget cap $78,015)
- Skyline Workspaces: 18 units due in 8 days (pretax budget cap $62,400)
- Blaze Collective: 26 units due in 8 days (pretax budget cap $92,593)
- Conduit Alliance: 20 units due in 8 days (pretax budget cap $67,591)
- Vantage Trust: 20 units due in 8 days (pretax budget cap $68,086)
- Catalyst Publishing: 18 units due in 9 days (pretax budget cap $61,158)
- Hartland Lyceum: 18 units due in 9 days (pretax budget cap $63,256)
- Pivot Cooperative: 19 units due in 9 days (pretax budget cap $68,085)
- Cipher Bureau: 22 units due in 9 days (pretax budget cap $77,501)
- Monarch Works: 18 units due in 9 days (pretax budget cap $60,217)
- Bayshore Innovations: 18 units due in 10 days (pretax budget cap $59,320)
- Onyx Ventures: 31 units due in 10 days (pretax budget cap $109,906)
- Lakewood Studios: 23 units due in 10 days (pretax budget cap $81,969)
- Flux Institute: 18 units due in 10 days (pretax budget cap $64,029)
- Forge Observatory: 32 units due in 10 days (pretax budget cap $114,905)
- Haven Hub: 28 units due in 10 days (pretax budget cap $100,377)
- Opal Manufactory: 24 units due in 10 days (pretax budget cap $81,258)
- Crestview Exchange: 19 units due in 11 days (pretax budget cap $64,466)
- Aegis Gallery: 19 units due in 11 days (pretax budget cap $62,793)
- Bronze Group: 18 units due in 11 days (pretax budget cap $62,504)
- Thornton Robotics: 25 units due in 12 days (pretax budget cap $83,226)
- Riverdale Theater: 19 units due in 12 days (pretax budget cap $68,445)
- Beacon Research: 31 units due in 12 days (pretax budget cap $103,918)
- Velocity Chambers: 18 units due in 12 days (pretax budget cap $64,281)
- Northbridge Arena: 22 units due in 13 days (pretax budget cap $78,025)
- Orbital Engineering: 32 units due in 13 days (pretax budget cap $106,549)
- Vertex Advisory: 28 units due in 13 days (pretax budget cap $92,710)
- Copper Designs: 25 units due in 13 days (pretax budget cap $89,403)
- Silverline Bazaar: 32 units due in 13 days (pretax budget cap $108,722)

We have 286 finished units on hand. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.7% at selling price.

## Background & Policy

* These are the rules for customer order acceptance.
* Accepted orders must allow at least 9 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For all accepted orders, arrange fulfillment at the lowest possible new purchase or manufacturing cost.
* The combined units covered through new purchasing or manufacturing must clear at least 27.7% portfolio-level new-spend margin at selling price.
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
