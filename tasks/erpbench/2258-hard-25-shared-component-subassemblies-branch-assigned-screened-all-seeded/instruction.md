**Priya Shah · Supply & Procurement · Teams**

Review the open order requests for CO2 Total Flooding System.

- Horizon Interactive: 18 units due in 8 days (pretax budget cap $187,459)
- Dune Gallery: 18 units due in 8 days (pretax budget cap $172,779)
- Quartz Research: 20 units due in 8 days (pretax budget cap $201,598)
- Vertex Studios West: 24 units due in 8 days (pretax budget cap $236,232)
- Solace Productions: 18 units due in 8 days (pretax budget cap $171,188)
- Catalyst Boutique: 18 units due in 9 days (pretax budget cap $186,556)
- Flint Robotics: 18 units due in 9 days (pretax budget cap $186,525)
- Garnet Initiative: 18 units due in 9 days (pretax budget cap $181,138)
- Baltic Pavilion: 18 units due in 9 days (pretax budget cap $171,325)
- Spark Clinics: 19 units due in 9 days (pretax budget cap $191,086)
- Alpine Solutions Group: 20 units due in 9 days (pretax budget cap $190,752)
- Flux Foundry: 18 units due in 10 days (pretax budget cap $177,491)
- Grove Sciences: 18 units due in 10 days (pretax budget cap $181,214)
- Indigo Forum: 21 units due in 10 days (pretax budget cap $218,838)
- Riverdale Innovations: 18 units due in 10 days (pretax budget cap $180,154)
- Prism Practice: 20 units due in 11 days (pretax budget cap $198,328)
- Stratos Studios South: 18 units due in 11 days (pretax budget cap $183,602)
- Coral Society: 18 units due in 11 days (pretax budget cap $176,411)
- Trellis Collective East: 19 units due in 11 days (pretax budget cap $197,596)
- Scion Collective: 19 units due in 11 days (pretax budget cap $192,687)
- Blaze Workshop: 20 units due in 12 days (pretax budget cap $201,259)
- Fairview Partners: 18 units due in 12 days (pretax budget cap $186,159)
- Slate Academy: 22 units due in 12 days (pretax budget cap $209,176)
- Granite Studios: 20 units due in 13 days (pretax budget cap $194,890)
- Cobalt Office: 18 units due in 13 days (pretax budget cap $177,718)
- Stonewall Refinery: 19 units due in 13 days (pretax budget cap $190,540)
- Citadel Manufactory: 18 units due in 13 days (pretax budget cap $185,371)

We have 206 finished units on hand. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 28.3% at selling price.

## Background & Policy

* These are the rules for customer order acceptance.
* Accepted orders must allow at least 11 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Deliver eligible orders but focus on reducing fresh procurement or manufacturing expenses.
* Any units you cover through new buying or manufacturing count toward one combined portfolio that must still meet a minimum 28.3% new-spend margin at selling price.
* Finance considers the existing stock as sunk cost.
* Some sales documents may already exist in draft; review existing documents before creating new ones.
* Cancel any already-drafted sales order that fails those acceptance rules.
* Customer budgets are pre-tax amounts.
* Link every accepted Sales Order to the related Manufacturing Orders and Purchase Orders for traceability.
* For finished goods POs, put the SO reference(s) (e.g. S00030 or S00030, S00031) into the origin field ('Source' in the UI).
* For component POs, put the MO reference(s) (e.g. WH/MO/00010 or WH/MO/00010, WH/MO/00011) into the origin field.
* For finished goods MOs, put the Sales Order reference (e.g. S00030) into the origin field ('Source' in the UI).
* For subassembly or intermediate MOs, put the immediate parent MO reference(s) that the subassembly feeds (e.g. WH/MO/00020 or WH/MO/00020, WH/MO/00021) into the origin field ('Source' in the UI).
* In the end, the lineage must be SO -> MO -> (Subassembly MO if needed) -> PO or SO -> PO for every incoming customer order you accept.
* You must sell this product at List Price.
* On every accepted Sales Order, set the commitment date.
* On manufacturing orders, you must set the start date and the due date.
* If you choose to manufacture, you must procure the components that are not in stock.
* On purchase orders, you must set the delivery date.
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

Fulfillment constraints for accepted orders:
- After an order is accepted, treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- For each component supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

Work in the `odoo` ERP and commit the plan there.
