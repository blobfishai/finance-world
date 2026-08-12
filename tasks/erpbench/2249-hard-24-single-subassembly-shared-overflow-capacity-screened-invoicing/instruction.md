**Priya Shah · Supply & Procurement · Teams**

Start with the live customer requests for Landing Door Assembly Single-Speed.

- Metro Atelier: 18 units due in 8 days (pretax budget cap $64,379)
- Fairview Exchange: 18 units due in 9 days (pretax budget cap $69,910)
- Ridge Enterprises: 14 units due in 9 days (pretax budget cap $50,549)
- Borough Boutique: 17 units due in 9 days (pretax budget cap $61,983)
- Copper Collective: 26 units due in 9 days (pretax budget cap $101,619)
- Blaze Creative: 19 units due in 13 days (pretax budget cap $71,422)
- Sierra Collective East: 26 units due in 13 days (pretax budget cap $94,284)
- Compass Pavilion: 25 units due in 13 days (pretax budget cap $93,097)
- Cipher Designs: 26 units due in 14 days (pretax budget cap $100,819)

We have 87 finished units on hand. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.1% at selling price. After fulfillment, create and post the required linked customer invoices. Use 30 Days terms on retained sales orders and all linked customer invoices.

## Background & Policy

* These are the rules for customer order acceptance.
* Accepted orders must request between 15 and 25 units.
* Reject or cancel any order that fails those acceptance rules.
* Once orders are accepted, cover them while limiting this cycle's purchasing to as few vendors as practical. When vendor counts tie, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 26.1% new-spend margin at selling price.
* Use available finished stock where it helps avoid opening additional purchasing paths.
* Some sales documents may already exist in draft; review existing documents before creating new ones.
* Cancel any already-drafted sales order that fails those acceptance rules.
* Customer budgets are pre-tax amounts.
* Link every accepted Sales Order to the related Manufacturing Orders and Purchase Orders for traceability.
* After confirming each retained sales order, create and post exactly one linked customer invoice.
* Use 30 Days terms on retained sales orders and all linked customer invoices.
* Rejected, cancelled, or skipped orders must not be invoiced.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Fulfillment constraints for accepted orders:
- After an order is accepted, treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- For each component supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
