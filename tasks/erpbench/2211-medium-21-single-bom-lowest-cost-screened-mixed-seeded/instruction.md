**Priya Shah · Supply & Procurement · Teams**

Start with the live customer requests for Vertical Form-Fill-Seal Machine.

- Meridian Advisory: 15 units due in 9 days (pretax budget cap $435,583)
- Titan Labs: 16 units due in 9 days (pretax budget cap $524,226)
- Flint Bazaar: 21 units due in 9 days (pretax budget cap $734,201)
- Orbital Dynamics: 22 units due in 10 days (pretax budget cap $762,674)
- Spectra Brands: 26 units due in 12 days (pretax budget cap $849,104)
- Ironwood Atelier: 19 units due in 13 days (pretax budget cap $663,254)
- Eclipse Boutique: 26 units due in 13 days (pretax budget cap $841,285)
- Catalyst Practice: 23 units due in 14 days (pretax budget cap $800,413)

On-hand finished stock covers 68 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.2% at selling price.

## Background & Policy

* Our criteria for accepting incoming customer orders are as follows.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must allow at least 10 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Once orders are accepted, cover them while limiting this cycle's purchasing to as few vendors as practical. When vendor counts tie, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 26.2% new-spend margin at selling price.
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
* Review Internal Notes/comments on stock, customers, vendors, and workcenters before you confirm entries in the ERP.

Fulfillment constraints for accepted orders:
- After an order is accepted, treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- For each component supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
