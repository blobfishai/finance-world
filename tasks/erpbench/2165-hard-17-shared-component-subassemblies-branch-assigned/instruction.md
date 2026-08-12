**Priya Shah · Supply & Procurement · Teams**

Supply plans must be created to fulfill each outstanding Standpipe and Hose System Package customer order listed.

- Metro Holdings: 29 units due in 8 days (pretax budget cap $120,286)
- Blaze Supply Co: 18 units due in 8 days (pretax budget cap $75,355)
- Westfield Enterprises: 31 units due in 8 days (pretax budget cap $123,862)
- Iron Studios: 20 units due in 9 days (pretax budget cap $85,618)
- Eclipse Forum: 21 units due in 9 days (pretax budget cap $83,847)
- Summit Consortium: 21 units due in 9 days (pretax budget cap $85,443)
- Lance Academy: 24 units due in 9 days (pretax budget cap $101,630)
- Globe Publishing: 18 units due in 10 days (pretax budget cap $76,020)
- Brookfield Reserve: 32 units due in 10 days (pretax budget cap $128,297)
- Arrow Manufactory: 25 units due in 10 days (pretax budget cap $104,098)
- Oxide Chambers: 20 units due in 10 days (pretax budget cap $81,130)
- Copper Museum: 18 units due in 10 days (pretax budget cap $77,731)
- Cipher Pavilion: 21 units due in 10 days (pretax budget cap $85,609)
- Flux Refinery: 32 units due in 10 days (pretax budget cap $134,956)
- Slate Studios South: 21 units due in 10 days (pretax budget cap $87,064)
- Citadel Works: 19 units due in 11 days (pretax budget cap $76,504)
- Apex Interactive: 26 units due in 11 days (pretax budget cap $109,084)
- Forge Hub: 29 units due in 11 days (pretax budget cap $116,761)
- Ironside Creative: 21 units due in 11 days (pretax budget cap $91,295)
- Redstone Practice: 21 units due in 11 days (pretax budget cap $88,721)
- Skyline Greenhouse: 20 units due in 11 days (pretax budget cap $80,170)
- Ironwood Cooperative: 18 units due in 12 days (pretax budget cap $76,037)
- Bronze Guild: 20 units due in 12 days (pretax budget cap $85,269)
- Terra Initiative: 22 units due in 12 days (pretax budget cap $88,823)
- Gateway Clinics: 24 units due in 12 days (pretax budget cap $96,645)
- Silverline Agency: 18 units due in 12 days (pretax budget cap $76,221)
- Sterling Collective East: 23 units due in 12 days (pretax budget cap $95,294)
- Hartland Lyceum: 32 units due in 13 days (pretax budget cap $133,911)

Current finished-goods stock is 258 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.3% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 28.3% new-spend margin at selling price.
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
