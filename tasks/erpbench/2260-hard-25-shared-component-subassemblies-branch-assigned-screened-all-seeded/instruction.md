**Priya Shah · Supply & Procurement · Teams**

Address the current order backlog for Foam Deluge System Package.

- Dune Fabricators: 18 units due in 8 days (pretax budget cap $157,962)
- Sterling Group: 21 units due in 8 days (pretax budget cap $193,569)
- Cobalt Alliance: 26 units due in 8 days (pretax budget cap $226,248)
- Catalyst Conservatory: 21 units due in 9 days (pretax budget cap $184,635)
- Slate Trust: 24 units due in 9 days (pretax budget cap $221,552)
- Cascade Collective East: 18 units due in 9 days (pretax budget cap $157,053)
- Axis Council: 21 units due in 10 days (pretax budget cap $186,434)
- Baseline Foundry: 20 units due in 10 days (pretax budget cap $180,395)
- Keystone Trading Co: 19 units due in 10 days (pretax budget cap $169,925)
- Matrix Analytics: 25 units due in 11 days (pretax budget cap $216,750)
- Peak Engineering: 20 units due in 11 days (pretax budget cap $182,683)
- Ironside Works: 18 units due in 11 days (pretax budget cap $167,895)
- Cardinal Exchange: 20 units due in 11 days (pretax budget cap $182,493)
- Sentinel Academy: 18 units due in 11 days (pretax budget cap $165,004)
- Haven Clinics: 32 units due in 12 days (pretax budget cap $297,303)
- Metro Studios East: 30 units due in 12 days (pretax budget cap $281,514)
- Flux Pictures: 23 units due in 12 days (pretax budget cap $217,932)
- Iron Observatory: 22 units due in 12 days (pretax budget cap $196,276)
- Comet Lyceum: 24 units due in 13 days (pretax budget cap $216,767)
- Lumen Interactive: 19 units due in 13 days (pretax budget cap $174,890)
- Osprey Brands: 23 units due in 13 days (pretax budget cap $206,353)

We have 185 finished units on hand. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.4% at selling price.

## Background & Policy

* Order acceptance must follow these rules.
* Accepted orders must allow at least 9 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Arrange supply for eligible orders, ensuring the least new investment.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 26.4% new-spend margin at selling price.
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
* Review Internal Notes/comments on stock, customers, vendors, and workcenters before you confirm entries in the ERP.

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
