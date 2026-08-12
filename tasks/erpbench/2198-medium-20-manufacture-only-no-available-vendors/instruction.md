**Priya Shah · Supply & Procurement · Teams**

Ensure all these Isolation Transformer 150kVA customer orders are supplied on schedule:

- Apex Workspaces: 26 units due in 9 days (pretax budget cap $269,062)
- Globe Reserve: 14 units due in 9 days (pretax budget cap $142,744)
- Lance Refinery: 24 units due in 9 days (pretax budget cap $235,481)
- Peak Institute: 26 units due in 9 days (pretax budget cap $261,042)
- Solace Exchange: 19 units due in 10 days (pretax budget cap $189,673)
- Lumen Office: 26 units due in 11 days (pretax budget cap $262,052)
- Summit Robotics: 17 units due in 13 days (pretax budget cap $175,780)
- Borough Pictures: 23 units due in 13 days (pretax budget cap $242,426)
- Oxide Arena: 19 units due in 13 days (pretax budget cap $193,804)
- Cipher Media: 26 units due in 14 days (pretax budget cap $257,742)

Current finished-goods stock is 34 units.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.5% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 28.5% portfolio-level new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
* You must create and confirm the necessary sales orders, manufacturing orders, and any component purchase orders needed for assembly.
* Customer budgets are pre-tax amounts.
* Link Sales Orders to the related Manufacturing Orders and Purchase Orders for traceability.
* Use in-house manufacturing to cover finished-goods shortfalls; purchase orders are only for components.
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> PO.
* You must sell this product at List Price.
* On sales orders, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* Procure only the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each component supplier offer, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
