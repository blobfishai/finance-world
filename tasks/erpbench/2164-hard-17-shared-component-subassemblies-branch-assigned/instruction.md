**Priya Shah · Supply & Procurement · Teams**

Supply plans must be created to fulfill each outstanding Standpipe and Hose System Package customer order listed.

- Flux Trust: 21 units due in 8 days (pretax budget cap $86,828)
- Cardinal Solutions Group: 28 units due in 8 days (pretax budget cap $111,751)
- Atlas Agency: 19 units due in 8 days (pretax budget cap $79,380)
- Nimbus Trading Co: 19 units due in 8 days (pretax budget cap $81,442)
- Ironside Conservatory: 20 units due in 8 days (pretax budget cap $80,497)
- Osprey Studios West: 19 units due in 9 days (pretax budget cap $82,165)
- Prism Workshop: 18 units due in 9 days (pretax budget cap $76,428)
- Echo Arena: 19 units due in 9 days (pretax budget cap $79,009)
- Slate Theater: 24 units due in 9 days (pretax budget cap $97,385)
- Iron Works: 19 units due in 10 days (pretax budget cap $81,779)
- Trellis Guild: 21 units due in 10 days (pretax budget cap $89,227)
- Bridgeway Productions: 19 units due in 10 days (pretax budget cap $80,149)
- Meridian Council: 25 units due in 10 days (pretax budget cap $102,563)
- Globe Outfitters: 21 units due in 11 days (pretax budget cap $87,782)
- Westfield Initiative: 19 units due in 11 days (pretax budget cap $79,641)
- Ridgeline Pavilion: 18 units due in 11 days (pretax budget cap $72,285)
- Thornton Media: 24 units due in 11 days (pretax budget cap $103,636)
- Nexus Chambers: 31 units due in 11 days (pretax budget cap $130,892)
- Sierra Workspaces: 25 units due in 12 days (pretax budget cap $102,013)
- Ledger Forum: 18 units due in 12 days (pretax budget cap $71,111)
- Opal Dynamics: 26 units due in 12 days (pretax budget cap $105,900)
- Crestview Academy: 18 units due in 12 days (pretax budget cap $71,586)
- Ironwood Consortium: 19 units due in 12 days (pretax budget cap $75,650)
- Jade Collective East: 22 units due in 12 days (pretax budget cap $88,592)
- Indigo Refinery: 21 units due in 12 days (pretax budget cap $88,631)
- Summit Sciences: 21 units due in 12 days (pretax budget cap $88,862)
- Haven Creative: 19 units due in 12 days (pretax budget cap $76,164)
- Sapphire Advisory: 32 units due in 13 days (pretax budget cap $129,398)
- Dune Research: 23 units due in 13 days (pretax budget cap $96,053)
- Coral Hub: 32 units due in 13 days (pretax budget cap $133,071)

On-hand finished stock covers 264 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.1% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.1% at selling price.
* Accounting treats the existing stock as sunk cost.
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
* Review Internal Notes/comments on stock, customers, vendors, and workcenters before you confirm entries in the ERP.

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
