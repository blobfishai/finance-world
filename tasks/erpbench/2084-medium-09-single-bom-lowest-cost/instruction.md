**Priya Shah · Supply & Procurement · Teams**

The following customer orders for Automatic Case Erector require confirmed supply to proceed with fulfillment:

- Globe Guild: 15 units due in 8 days (pretax budget cap $288,057)
- Orbital Workspaces: 17 units due in 9 days (pretax budget cap $330,006)
- Redstone Designs: 21 units due in 9 days (pretax budget cap $412,329)
- Clearwater Boutique: 15 units due in 10 days (pretax budget cap $302,677)
- Evergreen Interactive: 15 units due in 10 days (pretax budget cap $295,258)
- Apex Academy: 19 units due in 10 days (pretax budget cap $357,508)
- Oakmont Holdings: 26 units due in 11 days (pretax budget cap $514,313)
- Pacific Exchange: 26 units due in 12 days (pretax budget cap $529,956)
- Catalyst Manufactory: 26 units due in 13 days (pretax budget cap $522,156)

Current finished-goods stock is 88 units. Any shortfall can be handled with finished-goods buying, in-house manufacturing, or a mix that still satisfies policy.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 25% portfolio-level new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
* You must create and confirm the necessary sales orders, purchase orders, and/or manufacturing orders.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> PO or SO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* If you choose to manufacture, you must procure the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer, respect min/max quantities as horizon-wide totals.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
