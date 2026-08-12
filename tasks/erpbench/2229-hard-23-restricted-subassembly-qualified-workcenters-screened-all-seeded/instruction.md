**Priya Shah · Supply & Procurement · Teams**

Process the incoming customer orders for Solar Shingle Roof Tile Set.

- Orbital Academy: 15 units due in 8 days (pretax budget cap $18,975)
- Pivot Brands: 15 units due in 8 days (pretax budget cap $19,515)
- Crestview Atelier: 20 units due in 8 days (pretax budget cap $26,241)
- Iron Studios East: 17 units due in 8 days (pretax budget cap $22,670)
- Northbridge Trust: 19 units due in 9 days (pretax budget cap $23,764)
- Forge Interactive: 17 units due in 10 days (pretax budget cap $22,491)
- Skyline Archive: 15 units due in 10 days (pretax budget cap $19,786)
- Oakmont Architects: 14 units due in 10 days (pretax budget cap $14,465)
- Polar Trading Co: 21 units due in 14 days (pretax budget cap $27,381)

We have 33 finished units on hand. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.3% at selling price.

## Background & Policy

* Our criteria for accepting incoming customer orders are as follows.
* Only accept orders whose budgets cover the full list-price total.
* Reject or cancel any order that fails those acceptance rules.
* For every order that passes acceptance, provide coverage while consolidating this cycle's purchasing across as few vendors as practical. If more than one feasible plan uses the same number of vendors, keep new purchasing and manufacturing spend as low as possible.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.3% at selling price.
* Available finished stock can be used where it helps avoid adding another supplier to the plan.
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
