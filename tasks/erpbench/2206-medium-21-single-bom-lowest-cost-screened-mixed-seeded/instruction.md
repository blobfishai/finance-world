**Priya Shah · Supply & Procurement · Teams**

Fill the pending customer orders for Carton Sealer Top-Bottom.

- Meridian Alliance: 17 units due in 8 days (pretax budget cap $85,327)
- Osprey Academy: 20 units due in 9 days (pretax budget cap $124,441)
- Vertex Forum: 18 units due in 10 days (pretax budget cap $120,346)
- Gateway Reserve: 26 units due in 10 days (pretax budget cap $175,411)
- Westfield Refinery: 17 units due in 11 days (pretax budget cap $106,446)
- Stratos Clinics: 16 units due in 13 days (pretax budget cap $102,373)
- Northbridge Workspaces: 21 units due in 13 days (pretax budget cap $137,340)
- Lakewood Initiative: 14 units due in 13 days (pretax budget cap $92,300)
- Flux Hub: 25 units due in 14 days (pretax budget cap $163,974)
- Peak Fabricators: 26 units due in 14 days (pretax budget cap $165,714)

Current finished-goods stock is 91 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.9% at selling price.

## Background & Policy

* Customer order acceptance is based on the following criteria.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must allow at least 10 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For all accepted orders, arrange fulfillment while keeping this cycle's purchasing concentrated with as few vendors as practical. If vendor counts tie, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 27.9% new-spend margin at selling price.
* Use the finished stock on hand where it helps keep purchasing concentrated with fewer vendors.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Fulfillment constraints for accepted orders:
- After an order is accepted, treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- For each component supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
