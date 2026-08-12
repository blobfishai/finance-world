**Priya Shah · Supply & Procurement · Teams**

The following Centrifugal Compressor 200HP customer orders are firm and must be supplied on schedule:

- Nexus Guild: 18 units due in 8 days (pretax budget cap $978,433)
- Lumen Conservatory: 18 units due in 8 days (pretax budget cap $947,786)
- Forge Institute: 19 units due in 8 days (pretax budget cap $1,004,826)
- Fairview Innovations: 29 units due in 8 days (pretax budget cap $1,443,125)
- Spark Greenhouse: 19 units due in 8 days (pretax budget cap $1,030,443)
- Terra Publishing: 19 units due in 8 days (pretax budget cap $972,621)
- Ashford Productions: 18 units due in 9 days (pretax budget cap $920,046)
- Ironside Hub: 19 units due in 9 days (pretax budget cap $1,000,660)
- Grove Solutions Group: 22 units due in 9 days (pretax budget cap $1,168,937)
- Monarch Architects: 19 units due in 9 days (pretax budget cap $1,033,905)
- Mosaic Collective East: 18 units due in 10 days (pretax budget cap $961,163)
- Trellis Trust: 23 units due in 11 days (pretax budget cap $1,242,353)
- Beacon Cooperative: 21 units due in 11 days (pretax budget cap $1,104,909)
- Stonewall Interactive: 18 units due in 11 days (pretax budget cap $896,690)
- Northbridge Museum: 19 units due in 12 days (pretax budget cap $1,021,077)
- Blaze Holdings: 20 units due in 12 days (pretax budget cap $1,084,155)
- Onyx Studios South: 20 units due in 12 days (pretax budget cap $1,018,993)
- Alpine Studios East: 22 units due in 12 days (pretax budget cap $1,100,416)
- Hartland Media: 20 units due in 12 days (pretax budget cap $1,072,425)
- Arc Alliance: 22 units due in 12 days (pretax budget cap $1,195,812)
- Nimbus Ventures: 18 units due in 13 days (pretax budget cap $920,747)
- Ironwood Council: 22 units due in 13 days (pretax budget cap $1,130,782)
- Vertex Studios: 18 units due in 13 days (pretax budget cap $977,006)
- Cipher Robotics: 19 units due in 13 days (pretax budget cap $1,028,451)

On-hand finished stock covers 192 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.4% at selling price.

## Background & Policy

* Fulfill all customer orders while preserving as much shared workcenter capacity as possible for other scheduled work. If more than one feasible plan uses the same amount of workcenter capacity, keep new purchasing and manufacturing spend as low as possible.
* The combined units covered through new purchasing or manufacturing must clear at least 26.4% portfolio-level new-spend margin at selling price.
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
