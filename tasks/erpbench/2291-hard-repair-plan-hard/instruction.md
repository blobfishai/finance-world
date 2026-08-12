**Priya Shah · Supply & Procurement · Teams**

Existing confirmed sales orders and current manufacturing commitments for Bifacial Solar Module 450W are already in Odoo. Assembly Line 1 is experiencing an equipment outage, and confirmed manufacturing work is already scheduled on that line. Reuse the existing sales orders, review the commitments already in place, cancel the affected manufacturing orders, keep unaffected work where it still makes sense, and adjust the plan for Forge Guild, Bridgeway Bureau, Ivory Designs, Horizon Fabricators, Ironside Trust, and Quantum Dynamics using the best feasible alternative fulfillment route.

- Forge Guild: 15 units due in 8 days (pretax budget cap $6,438)
- Bridgeway Bureau: 15 units due in 8 days (pretax budget cap $6,894)
- Ivory Designs: 15 units due in 10 days (pretax budget cap $6,619)
- Horizon Fabricators: 16 units due in 10 days (pretax budget cap $7,009)
- Chrome Trading Co: 25 units due in 11 days (pretax budget cap $10,972)
- Ironside Trust: 15 units due in 11 days (pretax budget cap $6,412)
- Quantum Dynamics: 15 units due in 11 days (pretax budget cap $6,516)
- Baltic Arena: 22 units due in 12 days (pretax budget cap $9,378)
- Helix Enterprises: 18 units due in 12 days (pretax budget cap $7,969)
- Stonewall Cooperative: 15 units due in 12 days (pretax budget cap $6,844)
- Silverline Workshop: 16 units due in 12 days (pretax budget cap $6,848)

We have 52 finished units on hand. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.9% at selling price.

## Background & Policy

* Adjust the existing supply plan with the least disruption to what is already committed. When more than one feasible option changes the plan by the same amount, keep new purchasing and manufacturing spend as low as possible.
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
