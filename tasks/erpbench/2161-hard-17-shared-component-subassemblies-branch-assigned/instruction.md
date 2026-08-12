**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Dry Pipe Sprinkler System require confirmed supply to proceed with fulfillment:

- Blaze Group: 19 units due in 8 days (pretax budget cap $113,022)
- Forge Pavilion: 22 units due in 8 days (pretax budget cap $128,379)
- Spark Arena: 20 units due in 8 days (pretax budget cap $119,848)
- Matrix Observatory: 30 units due in 8 days (pretax budget cap $174,138)
- Compass Works: 18 units due in 9 days (pretax budget cap $108,299)
- Garnet Designs: 19 units due in 9 days (pretax budget cap $113,968)
- Stonewall Labs: 32 units due in 9 days (pretax budget cap $182,563)
- Echo Practice: 28 units due in 9 days (pretax budget cap $170,062)
- Zenith Collective: 24 units due in 9 days (pretax budget cap $140,222)
- Bayshore Manufactory: 19 units due in 10 days (pretax budget cap $109,360)
- Cosmo Greenhouse: 32 units due in 11 days (pretax budget cap $194,916)
- Chrome Interactive: 32 units due in 11 days (pretax budget cap $186,583)
- Brookfield Gallery: 22 units due in 11 days (pretax budget cap $131,615)
- Cobalt Archive: 21 units due in 11 days (pretax budget cap $129,146)
- Drift Academy: 23 units due in 11 days (pretax budget cap $134,155)
- Marble Systems: 19 units due in 11 days (pretax budget cap $113,553)
- Evergreen Brands: 32 units due in 11 days (pretax budget cap $195,541)
- Mosaic Analytics: 32 units due in 11 days (pretax budget cap $185,532)
- Anvil Trading Co: 18 units due in 11 days (pretax budget cap $105,626)
- Ledger Ventures: 18 units due in 11 days (pretax budget cap $111,601)
- Crest Workshop: 22 units due in 12 days (pretax budget cap $132,165)
- Osprey Dynamics: 19 units due in 12 days (pretax budget cap $110,270)
- Trident Hub: 18 units due in 12 days (pretax budget cap $109,093)
- Lakewood Workspaces: 21 units due in 12 days (pretax budget cap $127,574)
- Metro Fabricators: 30 units due in 12 days (pretax budget cap $172,392)
- Haven Technologies: 32 units due in 13 days (pretax budget cap $191,841)
- Titan Reserve: 32 units due in 13 days (pretax budget cap $196,937)
- Aegis Conservatory: 32 units due in 13 days (pretax budget cap $186,232)
- Quartz Exchange: 32 units due in 13 days (pretax budget cap $194,566)
- Ridgeline Enterprises: 32 units due in 13 days (pretax budget cap $191,183)

We have 300 finished units on hand. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.4% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 28.4% new-spend margin at selling price.
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
