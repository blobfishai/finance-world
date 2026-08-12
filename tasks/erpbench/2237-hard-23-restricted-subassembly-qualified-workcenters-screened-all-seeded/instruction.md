**Priya Shah · Supply & Procurement · Teams**

Review the open order requests for Bifacial Solar Module 450W.

- Oxide Exchange: 16 units due in 8 days (pretax budget cap $6,908)
- Hartland Holdings: 14 units due in 8 days (pretax budget cap $5,376)
- Granite Consortium: 20 units due in 9 days (pretax budget cap $8,643)
- Flux Trust: 17 units due in 9 days (pretax budget cap $7,063)
- Steel Trading Co: 23 units due in 10 days (pretax budget cap $10,331)
- Clearwater Interactive: 26 units due in 10 days (pretax budget cap $11,404)
- Vantage Council: 26 units due in 13 days (pretax budget cap $10,785)
- Sapphire Productions: 26 units due in 13 days (pretax budget cap $11,034)
- Onyx Boutique: 26 units due in 14 days (pretax budget cap $11,399)
- Lance Architects: 26 units due in 14 days (pretax budget cap $11,513)

Current finished-goods stock is 50 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.6% at selling price.

## Background & Policy

* The rules for which orders can be accepted are outlined below.
* Only accept orders whose budgets cover the full list-price total.
* Reject or cancel any order that fails those acceptance rules.
* For all accepted orders, arrange fulfillment while keeping this cycle's purchasing concentrated with as few vendors as practical. If vendor counts tie, keep new purchasing and manufacturing spend as low as possible.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.6% at selling price.
* Use the finished stock on hand where it helps keep purchasing concentrated with fewer vendors.
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
