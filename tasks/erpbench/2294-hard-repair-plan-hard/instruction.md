**Priya Shah · Supply & Procurement · Teams**

Existing confirmed sales orders and current manufacturing commitments for Ground-Mount Tracker System are already in Odoo. Assembly Line 1 is experiencing an equipment outage, and confirmed manufacturing work is already scheduled on that line. Reuse the existing sales orders, review the commitments already in place, cancel the affected manufacturing orders, keep unaffected work where it still makes sense, and adjust the plan for Apex Archive, Bridgeway Cooperative, Horizon Office, Oakmont Media, and Copper Arena using the best feasible alternative fulfillment route.

- Apex Archive: 17 units due in 8 days (pretax budget cap $92,928)
- Bridgeway Cooperative: 24 units due in 8 days (pretax budget cap $126,402)
- Horizon Office: 27 units due in 9 days (pretax budget cap $136,977)
- Oakmont Media: 15 units due in 9 days (pretax budget cap $79,435)
- Ironside Pictures: 16 units due in 10 days (pretax budget cap $86,905)
- Opal Museum: 20 units due in 10 days (pretax budget cap $108,159)
- Copper Arena: 27 units due in 10 days (pretax budget cap $137,329)
- Crest Lyceum: 20 units due in 11 days (pretax budget cap $102,960)
- Sierra Studios West: 27 units due in 12 days (pretax budget cap $138,421)
- Cobalt Fabricators: 27 units due in 12 days (pretax budget cap $144,834)

Current finished-goods stock is 60 units. If stock is not enough, you can cover the gap by buying finished goods, building in-house, or using a mix of both.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.9% at selling price.

## Background & Policy

* Work through the disruption with the smallest practical change to the commitments already in place. If multiple feasible options preserve the same amount of prior work, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 26.9% new-spend margin at selling price.
* Accounting treats the existing stock as sunk cost.
* The listed customer sales orders are already confirmed in Odoo; work from those orders and do not create duplicates.
* Review the current purchase orders, manufacturing orders, and supplier or workcenter notes before making changes.
* Keep commitments that still work; only rework the part of the plan affected by the disruption.
* Confirmed manufacturing work is already scheduled on Assembly Line 1, but that workcenter is experiencing an equipment outage.
* Cancel the affected manufacturing orders and cover the gap with the best feasible alternative fulfillment route without using that workcenter.
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

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- Assembly Line 1 is experiencing an equipment outage and must not be used.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
