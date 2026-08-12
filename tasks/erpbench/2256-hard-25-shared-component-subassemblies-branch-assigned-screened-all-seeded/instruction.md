**Priya Shah · Supply & Procurement · Teams**

Address the current order backlog for Wet Sprinkler System Package.

- Atlas Arena: 26 units due in 8 days (pretax budget cap $137,643)
- Slate Productions: 24 units due in 8 days (pretax budget cap $123,727)
- Pinnacle Hub: 18 units due in 8 days (pretax budget cap $101,254)
- Terra Chambers: 18 units due in 8 days (pretax budget cap $93,488)
- Keystone Academy: 20 units due in 8 days (pretax budget cap $106,832)
- Osprey Partners: 32 units due in 9 days (pretax budget cap $175,016)
- Mosaic Practice: 19 units due in 9 days (pretax budget cap $104,208)
- Riverdale Alliance: 32 units due in 9 days (pretax budget cap $173,834)
- Ironside Interactive: 20 units due in 9 days (pretax budget cap $103,967)
- Compass Supply Co: 21 units due in 9 days (pretax budget cap $113,440)
- Ember Office: 32 units due in 9 days (pretax budget cap $166,645)
- Sterling Collective: 31 units due in 9 days (pretax budget cap $167,168)
- Spire Conservatory: 23 units due in 10 days (pretax budget cap $125,858)
- Equinox Systems: 32 units due in 10 days (pretax budget cap $178,292)
- Aurora Designs: 18 units due in 10 days (pretax budget cap $98,060)
- Baltic Research: 26 units due in 10 days (pretax budget cap $136,651)
- Blaze Workshop: 32 units due in 10 days (pretax budget cap $175,434)
- Crown Trading Co: 25 units due in 11 days (pretax budget cap $132,247)
- Grove Atelier: 19 units due in 11 days (pretax budget cap $103,474)
- Cedar Architects: 22 units due in 11 days (pretax budget cap $122,187)
- Apex Archive: 26 units due in 11 days (pretax budget cap $143,317)
- Vertex Institute: 24 units due in 11 days (pretax budget cap $133,901)
- Jade Media: 19 units due in 12 days (pretax budget cap $101,010)
- Noble Pictures: 20 units due in 12 days (pretax budget cap $109,418)
- Opal Forum: 29 units due in 12 days (pretax budget cap $160,657)
- Baseline Society: 32 units due in 12 days (pretax budget cap $167,406)
- Orbital Engineering: 32 units due in 12 days (pretax budget cap $173,405)
- Fairview Clinics: 32 units due in 13 days (pretax budget cap $176,320)
- Aether Studios South: 32 units due in 13 days (pretax budget cap $164,911)
- Anvil Cooperative: 32 units due in 13 days (pretax budget cap $174,934)
- Zenith Creative: 32 units due in 13 days (pretax budget cap $168,891)
- Cardinal Outfitters: 32 units due in 13 days (pretax budget cap $177,792)

On-hand finished stock covers 333 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 30% at selling price.

## Background & Policy

* Customer order acceptance will be determined as follows.
* Accepted orders must allow at least 9 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* For all accepted orders, arrange fulfillment at the lowest possible new purchase or manufacturing cost.
* The combined units covered through new purchasing or manufacturing must clear at least 30% portfolio-level new-spend margin at selling price.
* Existing stock is a sunk cost and should not be treated as new spend.
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
* Before releasing anything, read the Internal Notes/comments on stock, customers, vendors, and workcenters.

Fulfillment constraints for accepted orders:
- After an order is accepted, treat workcenter capacity as a hard horizon-wide limit across all products that share the center.
- Check each workcenter's Internal Notes in Odoo for the exact horizon-wide minute limit.
- Assign workcenter on each manufacturing work order.
- For each finished-goods supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- For each component supplier offer used to fulfill accepted orders, respect min/max quantities as horizon-wide totals.
- Use one consolidated PO per supplier offer when fulfilling accepted orders (do not split a single offer across multiple POs).
- Check each vendor's Internal Notes in Odoo for fulfillment-side maximum order quantity limits.

---

Work in the `odoo` ERP. When the plan is committed, reply with `submit_answer`:

- `orders_accepted` (number)
- `orders_rejected` (number)
- `units_purchased` (number)
- `units_manufactured` (number)
- `assembly_cost` (number)
