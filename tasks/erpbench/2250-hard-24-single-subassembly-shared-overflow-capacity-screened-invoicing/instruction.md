**Priya Shah · Supply & Procurement · Teams**

Work through the current order queue for Elevator Cab Interior Module.

- Cobalt Greenhouse: 16 units due in 8 days (pretax budget cap $76,673)
- Trellis Systems: 17 units due in 9 days (pretax budget cap $86,735)
- Vertex Chambers: 16 units due in 11 days (pretax budget cap $80,061)
- Northbridge Bureau: 14 units due in 12 days (pretax budget cap $67,684)
- Ledger Atelier: 15 units due in 13 days (pretax budget cap $72,066)
- Granite Ventures: 16 units due in 14 days (pretax budget cap $78,928)
- Equinox Studios East: 18 units due in 14 days (pretax budget cap $87,861)
- Pinnacle Hub: 15 units due in 14 days (pretax budget cap $71,486)
- Cardinal Consortium: 17 units due in 14 days (pretax budget cap $81,572)

On-hand finished stock covers 68 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.8% at selling price. After fulfillment, create and post the required linked customer invoices. Use 30 Days terms on retained sales orders and all linked customer invoices.

## Background & Policy

* Order acceptance must follow these rules.
* Accepted orders must request between 15 and 16 units.
* Reject or cancel any order that fails those acceptance rules.
* For every order that passes acceptance, provide coverage while consolidating this cycle's purchasing across as few vendors as practical. If more than one feasible plan uses the same number of vendors, keep new purchasing and manufacturing spend as low as possible.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.8% at selling price.
* Available finished stock can be used where it helps avoid adding another supplier to the plan.
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
