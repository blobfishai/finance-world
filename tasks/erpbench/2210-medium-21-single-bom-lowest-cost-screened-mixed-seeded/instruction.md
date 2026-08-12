**Priya Shah · Supply & Procurement · Teams**

Process the incoming customer orders for Checkweigher Inline Module.

- Spark Interactive: 14 units due in 10 days (pretax budget cap $120,497)
- Opal Guild: 16 units due in 10 days (pretax budget cap $193,523)
- Northbridge Trust: 16 units due in 11 days (pretax budget cap $191,354)
- Horizon Studios West: 16 units due in 12 days (pretax budget cap $195,349)
- Bridgeway Research: 26 units due in 13 days (pretax budget cap $313,042)
- Catalyst Ventures: 15 units due in 13 days (pretax budget cap $184,472)
- Echo Gallery: 14 units due in 14 days (pretax budget cap $173,908)
- Sentinel Pavilion: 23 units due in 14 days (pretax budget cap $273,377)
- Drift Bazaar: 22 units due in 14 days (pretax budget cap $270,833)

Current finished-goods stock is 70 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.6% at selling price.

## Background & Policy

* Our criteria for accepting incoming customer orders are as follows.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must allow at least 11 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Once orders are accepted, cover them while limiting this cycle's purchasing to as few vendors as practical. When vendor counts tie, keep new purchasing and manufacturing spend as low as possible.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.6% at selling price.
* Use available finished stock where it helps avoid opening additional purchasing paths.
* Some sales documents may already exist in draft; review existing documents before creating new ones.
* Cancel any already-drafted sales order that fails those acceptance rules.
* Customer budgets are pre-tax amounts.
* Link every accepted Sales Order to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> PO or SO -> PO for every incoming customer order you accept.
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
