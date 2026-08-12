**Priya Shah · Supply & Procurement · Teams**

All orders below for Commercial Rooftop Array 10kW need confirmed supply coverage and scheduling.

- Slate Group: 24 units due in 8 days (pretax budget cap $229,331)
- Westfield Institute: 14 units due in 8 days (pretax budget cap $135,009)
- Titan Outfitters: 22 units due in 8 days (pretax budget cap $210,318)
- Sentinel Atelier: 16 units due in 8 days (pretax budget cap $145,693)
- Fairview Foundry: 16 units due in 9 days (pretax budget cap $141,456)
- Quantum Museum: 15 units due in 9 days (pretax budget cap $136,873)
- Pivot Technologies: 26 units due in 10 days (pretax budget cap $240,327)
- Bayshore Chambers: 17 units due in 10 days (pretax budget cap $157,402)
- Equinox Alliance: 17 units due in 11 days (pretax budget cap $162,722)
- Lumen Bureau: 23 units due in 13 days (pretax budget cap $209,956)

Current finished-goods stock is 41 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.4% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.4% new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
* You must create and confirm the necessary sales orders, purchase orders, and/or manufacturing orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* For subassembly or intermediate MOs, put the immediate parent MO reference(s) that the subassembly feeds (e.g. WH/MO/00020 or WH/MO/00020, WH/MO/00021) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> (Subassembly MO if needed) -> PO or SO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* If you choose to manufacture, you must procure the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Review Internal Notes/comments on stock, customers, vendors, and workcenters before you confirm entries in the ERP.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
