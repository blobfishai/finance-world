**Priya Shah · Supply & Procurement · Teams**

Existing confirmed sales orders and current manufacturing commitments for Ground-Mount Tracker System are already in Odoo. Assembly Line 1 is experiencing an equipment outage, and confirmed manufacturing work is already scheduled on that line. Reuse the existing sales orders, review the commitments already in place, cancel the affected manufacturing orders, keep unaffected work where it still makes sense, and adjust the plan for Monarch Studios, Lance Publishing, Grove Practice, Globe Manufactory, and Quartz Studios East using the best feasible alternative fulfillment route.

- Monarch Studios: 16 units due in 8 days (pretax budget cap $90,903)
- Lance Publishing: 22 units due in 8 days (pretax budget cap $121,238)
- Grove Practice: 18 units due in 8 days (pretax budget cap $107,342)
- Globe Manufactory: 18 units due in 8 days (pretax budget cap $106,611)
- Meridian Office: 27 units due in 8 days (pretax budget cap $156,328)
- Quartz Studios East: 23 units due in 10 days (pretax budget cap $132,464)
- Ironwood Outfitters: 17 units due in 11 days (pretax budget cap $100,303)
- Orbital Systems: 19 units due in 12 days (pretax budget cap $107,780)
- Opal Group: 18 units due in 12 days (pretax budget cap $105,598)
- Onyx Boutique: 22 units due in 12 days (pretax budget cap $125,307)

We have 56 finished units on hand. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.6% at selling price.

## Background & Policy

* Keep the committed orders on track while changing as little of the current plan as practical. If more than one feasible option preserves the same amount of prior work, keep new purchasing and manufacturing spend as low as possible.
* The combined units covered through new purchasing or manufacturing must clear at least 26.6% portfolio-level new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

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
