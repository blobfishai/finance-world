**Priya Shah · Supply & Procurement · Teams**

Start with the live customer requests for Stretch Wrapper Turntable Unit.

- Clearwater Consortium: 17 units due in 8 days (pretax budget cap $150,029)
- Baseline Forum: 14 units due in 8 days (pretax budget cap $103,448)
- Ember Foundry: 15 units due in 11 days (pretax budget cap $132,950)
- Opal Technologies: 18 units due in 11 days (pretax budget cap $165,324)
- Copper Refinery: 26 units due in 12 days (pretax budget cap $243,638)
- Oakmont Clinics: 26 units due in 12 days (pretax budget cap $240,135)
- Forge Manufactory: 26 units due in 13 days (pretax budget cap $237,265)
- Northbridge Enterprises: 26 units due in 14 days (pretax budget cap $232,506)

On-hand finished stock covers 71 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.2% at selling price.

## Background & Policy

* The rules for which orders can be accepted are outlined below.
* Only accept orders whose budgets cover the full list-price total.
* Accepted orders must allow at least 12 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For every order that passes acceptance, provide coverage while consolidating this cycle's purchasing across as few vendors as practical. If more than one feasible plan uses the same number of vendors, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 26.2% new-spend margin at selling price.
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
