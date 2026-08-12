**Priya Shah · Supply & Procurement · Teams**

Existing confirmed sales orders and current supply commitments for Ceiling Acoustic Baffle are already in Odoo. Cosmo Logistics has canceled on us, so that confirmed purchase order can no longer be relied on. Reuse the existing sales orders, review the commitments already in place, cancel that purchase order, keep unaffected work where it still makes sense, and adjust the plan for Quartz Exchange and Monarch Lyceum using the best feasible alternative source or fulfillment route.

- Marble Solutions Group: 6 units due in 6 days (pretax budget cap $2,072)
- Crestview Initiative: 11 units due in 6 days (pretax budget cap $3,788)
- Quartz Exchange: 11 units due in 7 days (pretax budget cap $3,649)
- Monarch Lyceum: 8 units due in 8 days (pretax budget cap $2,662)

On-hand finished stock covers 5 units. There is no in-house manufacturing route for the finished product, so any shortfall has to come from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 29.9% at selling price.

## Background & Policy

* Work through the disruption with the smallest practical change to the commitments already in place. If multiple feasible options preserve the same amount of prior work, keep new purchasing and manufacturing spend as low as possible.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 29.9% new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
* The listed customer sales orders are already confirmed in Odoo; work from those orders and do not create duplicates.
* Review the current purchase orders, manufacturing orders, and supplier or workcenter notes before making changes.
* Keep commitments that still work; only rework the part of the plan affected by the disruption.
* A confirmed purchase order from Cosmo Logistics is already in Odoo, but the supplier has canceled on us.
* Cancel that purchase order and cover the gap with the best feasible alternative source or fulfillment route without sending the same demand back down that supplier path.
* Link every accepted Sales Order to the related Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> PO for every incoming customer order you accept.
* You must sell this product at List Price.
* On every accepted Sales Order, set the commitment date.
* On purchase orders, you must set the delivery date.
* Before releasing anything, read the Internal Notes/comments on stock, customers, and vendors.

Capacity constraints:
- No in-house manufacturing capacity is available.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- That supplier commitment has fallen through and must not be reused.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
