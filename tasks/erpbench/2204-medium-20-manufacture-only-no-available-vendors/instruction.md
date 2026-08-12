**Priya Shah · Supply & Procurement · Teams**

Each customer order below requires a fulfillment-ready supply solution before its delivery due date:

- Oxide Institute: 16 units due in 10 days (pretax budget cap $252,544)
- Ironwood Academy: 17 units due in 10 days (pretax budget cap $271,487)
- Steel Supply Co: 26 units due in 10 days (pretax budget cap $424,946)
- Eclipse Ventures: 25 units due in 11 days (pretax budget cap $399,812)
- Prism Collective East: 26 units due in 11 days (pretax budget cap $421,523)
- Cascade Bureau: 26 units due in 11 days (pretax budget cap $411,020)
- Granite Archive: 26 units due in 12 days (pretax budget cap $401,055)
- Globe Systems: 26 units due in 12 days (pretax budget cap $417,484)
- Baltic Agency: 26 units due in 13 days (pretax budget cap $406,228)
- Westfield Analytics: 26 units due in 14 days (pretax budget cap $396,341)

Current finished-goods stock is 42 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.2% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.2% at selling price.
* Accounting treats the existing stock as sunk cost.
* You must create and confirm the necessary sales orders, manufacturing orders, and any component purchase orders needed for assembly.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* Use in-house manufacturing to cover finished-goods shortfalls; purchase orders are only for components.
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* Procure only the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Review Internal Notes/comments on stock, customers, vendors, and workcenters before you confirm entries in the ERP.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
