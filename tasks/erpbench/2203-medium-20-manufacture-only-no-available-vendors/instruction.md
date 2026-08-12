**Priya Shah · Supply & Procurement · Teams**

The following Dry-Type Transformer 500kVA customer orders are firm and must be supplied on schedule:

- Ledger Clinics: 14 units due in 8 days (pretax budget cap $290,849)
- Oakmont Analytics: 15 units due in 10 days (pretax budget cap $298,868)
- Sapphire Research: 15 units due in 11 days (pretax budget cap $318,630)
- Matrix Office: 20 units due in 11 days (pretax budget cap $391,733)
- Anvil Pavilion: 18 units due in 12 days (pretax budget cap $373,327)
- Orbital Collective: 15 units due in 12 days (pretax budget cap $316,742)
- Flux Initiative: 14 units due in 13 days (pretax budget cap $278,105)
- Helix Forum: 25 units due in 13 days (pretax budget cap $485,607)
- Iron Reserve: 17 units due in 13 days (pretax budget cap $358,936)

We have 28 finished units on hand.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.2% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.2% at selling price.
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
