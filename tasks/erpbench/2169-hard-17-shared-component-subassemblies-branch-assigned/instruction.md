**Priya Shah · Supply & Procurement · Teams**

Plan fulfillment for these outstanding CO2 Total Flooding System orders to ensure timely deliveries:

- Bronze Theater: 18 units due in 8 days (pretax budget cap $195,445)
- Alpine Institute: 18 units due in 8 days (pretax budget cap $187,209)
- Titan Chambers: 18 units due in 8 days (pretax budget cap $193,597)
- Aegis Robotics: 18 units due in 8 days (pretax budget cap $187,822)
- Terra Practice: 24 units due in 8 days (pretax budget cap $257,896)
- Globe Greenhouse: 19 units due in 8 days (pretax budget cap $207,515)
- Monarch Clinics: 18 units due in 9 days (pretax budget cap $193,882)
- Scion Alliance: 22 units due in 9 days (pretax budget cap $236,633)
- Haven Advisory: 28 units due in 9 days (pretax budget cap $296,498)
- Pacific Society: 21 units due in 9 days (pretax budget cap $232,647)
- Marble Foundry: 19 units due in 9 days (pretax budget cap $211,051)
- Comet Workshop: 18 units due in 10 days (pretax budget cap $194,255)
- Aurora Hub: 21 units due in 10 days (pretax budget cap $229,931)
- Drift Interactive: 19 units due in 10 days (pretax budget cap $210,120)
- Stratos Trust: 18 units due in 10 days (pretax budget cap $189,696)
- Lumen Creative: 18 units due in 10 days (pretax budget cap $188,993)
- Onyx Outfitters: 20 units due in 10 days (pretax budget cap $220,662)
- Ironside Trading Co: 22 units due in 12 days (pretax budget cap $231,457)
- Silverline Guild: 18 units due in 12 days (pretax budget cap $197,537)
- Coral Boutique: 21 units due in 12 days (pretax budget cap $227,833)
- Raven Bureau: 23 units due in 12 days (pretax budget cap $247,178)
- Cardinal Archive: 18 units due in 12 days (pretax budget cap $186,242)
- Ledger Gallery: 28 units due in 12 days (pretax budget cap $309,232)
- Conduit Workspaces: 18 units due in 12 days (pretax budget cap $194,958)
- Prism Brands: 18 units due in 12 days (pretax budget cap $186,794)
- Circuit Architects: 19 units due in 13 days (pretax budget cap $203,475)
- Peak Studios North: 18 units due in 13 days (pretax budget cap $199,900)
- Blaze Supply Co: 20 units due in 13 days (pretax budget cap $205,245)

We have 224 finished units on hand. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.3% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 25.3% new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
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
