**Priya Shah · Supply & Procurement · Teams**

The following Cast Resin Transformer 300kVA customer orders are firm and must be supplied on schedule:

- Spire Dynamics: 26 units due in 8 days (pretax budget cap $417,450)
- Borough Systems: 19 units due in 8 days (pretax budget cap $329,231)
- Prism Trading Co: 16 units due in 8 days (pretax budget cap $263,740)
- Arc Fabricators: 21 units due in 9 days (pretax budget cap $337,137)
- Gateway Creative: 25 units due in 10 days (pretax budget cap $418,411)
- Blaze Solutions Group: 20 units due in 11 days (pretax budget cap $341,030)
- Eclipse Practice: 15 units due in 12 days (pretax budget cap $253,413)
- Conduit Lyceum: 14 units due in 12 days (pretax budget cap $224,099)
- Opal Archive: 24 units due in 14 days (pretax budget cap $387,439)
- Granite Pictures: 20 units due in 14 days (pretax budget cap $324,002)

We have 34 finished units on hand.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 25.7% at selling price.

## Background & Policy

* Fulfill all orders while minimizing new spending on procurement and manufacturing.
* The combined units covered through new purchasing or manufacturing must clear at least 25.7% portfolio-level new-spend margin at selling price.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Capacity constraints:
- Treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
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
