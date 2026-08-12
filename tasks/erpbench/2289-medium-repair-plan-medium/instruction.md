**Priya Shah · Supply & Procurement · Teams**

Existing confirmed sales orders and current supply commitments for Emergency Exit Combo Fixture are already in Odoo. Northbridge Manufacturing has canceled on us, so that confirmed purchase order can no longer be relied on. Reuse the existing sales orders, review the commitments already in place, cancel that purchase order, keep unaffected work where it still makes sense, and adjust the plan for Noble Collective and Sierra Engineering using the best feasible alternative source or fulfillment route.

- Baltic Alliance: 9 units due in 7 days (pretax budget cap $1,852)
- Thornton Sciences: 13 units due in 7 days (pretax budget cap $2,609)
- Noble Collective: 13 units due in 9 days (pretax budget cap $2,694)
- Sierra Engineering: 13 units due in 10 days (pretax budget cap $2,616)

Current finished-goods stock is 5 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 24.8% at selling price.

## Background & Policy

* Keep the committed orders on track while changing as little of the current plan as practical. If more than one feasible option preserves the same amount of prior work, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 24.8% new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
* The listed customer sales orders are already confirmed in Odoo; work from those orders and do not create duplicates.
* Review the current purchase orders, manufacturing orders, and supplier or workcenter notes before making changes.
* Keep commitments that still work; only rework the part of the plan affected by the disruption.
* A confirmed purchase order from Northbridge Manufacturing is already in Odoo, but the supplier has canceled on us.
* Cancel that purchase order and cover the gap with the best feasible alternative source or fulfillment route without sending the same demand back down that supplier path.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- That supplier commitment has fallen through and must not be reused.
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
