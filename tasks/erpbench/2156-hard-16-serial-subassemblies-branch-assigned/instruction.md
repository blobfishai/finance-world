**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Booster Compressor 500PSI require confirmed supply to proceed with fulfillment:

- Stonewall Media: 20 units due in 8 days (pretax budget cap $594,339)
- Nexus Atelier: 18 units due in 8 days (pretax budget cap $519,815)
- Ember Systems: 18 units due in 9 days (pretax budget cap $529,794)
- Ridge Cooperative: 22 units due in 9 days (pretax budget cap $670,957)
- Slate Advisory: 21 units due in 9 days (pretax budget cap $605,677)
- Keystone Trust: 20 units due in 10 days (pretax budget cap $595,752)
- Drift Interactive: 22 units due in 10 days (pretax budget cap $667,236)
- Osprey Group: 22 units due in 11 days (pretax budget cap $630,417)
- Garnet Workspaces: 19 units due in 11 days (pretax budget cap $560,808)
- Cascade Engineering: 20 units due in 11 days (pretax budget cap $608,813)
- Arrow Council: 30 units due in 12 days (pretax budget cap $856,569)
- Equinox Office: 32 units due in 12 days (pretax budget cap $917,956)
- Ashford Initiative: 32 units due in 12 days (pretax budget cap $948,428)
- Vantage Exchange: 32 units due in 13 days (pretax budget cap $961,910)
- Prism Archive: 32 units due in 13 days (pretax budget cap $988,461)
- Vertex Forum: 32 units due in 13 days (pretax budget cap $962,332)
- Alpine Chambers: 32 units due in 13 days (pretax budget cap $937,774)
- Skyline Publishing: 32 units due in 13 days (pretax budget cap $973,897)
- Opal Studios West: 32 units due in 13 days (pretax budget cap $962,300)
- Horizon Clinics: 32 units due in 13 days (pretax budget cap $927,195)

We have 208 finished units on hand. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.4% at selling price.

## Background & Policy

* Get every customer order covered while keeping as much shared workcenter capacity open as possible. Keep new purchasing and manufacturing spend as low as possible when workcenter-capacity use ties.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.4% at selling price.
* Use the finished stock on hand where it helps reduce demand on shared workcenters.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
