**Priya Shah · Supply & Procurement · Teams**

Existing confirmed sales orders and current supply commitments for Conference Pod Enclosure are already in Odoo. Iron Transport has canceled on us, so that confirmed purchase order can no longer be relied on. Reuse the existing sales orders, review the commitments already in place, cancel that purchase order, keep unaffected work where it still makes sense, and adjust the plan for Cipher Ventures, Jade Productions, Flint Studios North, and Ashford Workshop using the best feasible alternative source or fulfillment route.

- Cipher Ventures: 7 units due in 7 days (pretax budget cap $6,200)
- Jade Productions: 11 units due in 7 days (pretax budget cap $9,245)
- Flint Studios North: 11 units due in 9 days (pretax budget cap $9,529)
- Ashford Workshop: 11 units due in 9 days (pretax budget cap $9,307)

We have 6 finished units on hand. The finished product is not manufactured in-house, so any shortfall has to be sourced from vendors.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 27.6% at selling price.

## Background & Policy

* Work through the disruption with the smallest practical change to the commitments already in place. If multiple feasible options preserve the same amount of prior work, keep new purchasing and manufacturing spend as low as possible.
* The combined units covered through new purchasing or manufacturing must clear at least 27.6% portfolio-level new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
* The listed customer sales orders are already confirmed in Odoo; work from those orders and do not create duplicates.
* Review the current purchase orders, manufacturing orders, and supplier or workcenter notes before making changes.
* Keep commitments that still work; only rework the part of the plan affected by the disruption.
* A confirmed purchase order from Iron Transport is already in Odoo, but the supplier has canceled on us.
* Cancel that purchase order and cover the gap with the best feasible alternative source or fulfillment route without sending the same demand back down that supplier path.
* Link every accepted Sales Order to the related Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> PO for every incoming customer order you accept.
* You must sell this product at List Price.
* On every accepted Sales Order, set the commitment date.
* On purchase orders, you must set the delivery date.
* Check Internal Notes/comments on stock, customers, and vendors before you release anything.

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
