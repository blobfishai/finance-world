**Priya Shah · Supply & Procurement · Teams**

Handle the open Foam Deluge System Package order queue.

- Steel Council: 29 units due in 8 days (pretax budget cap $264,978)
- Coral Lyceum: 26 units due in 8 days (pretax budget cap $240,436)
- Bronze Chambers: 19 units due in 9 days (pretax budget cap $173,892)
- Echo Works: 21 units due in 9 days (pretax budget cap $188,640)
- Quartz Systems: 29 units due in 9 days (pretax budget cap $253,749)
- Lakewood Designs: 19 units due in 10 days (pretax budget cap $169,079)
- Zenith Interactive: 21 units due in 10 days (pretax budget cap $187,340)
- Thornton Forum: 19 units due in 10 days (pretax budget cap $178,269)
- Pacific Research: 19 units due in 10 days (pretax budget cap $167,027)
- Anvil Studios North: 20 units due in 10 days (pretax budget cap $180,108)
- Canton Exchange: 18 units due in 10 days (pretax budget cap $166,456)
- Pinnacle Partners: 18 units due in 11 days (pretax budget cap $160,048)
- Cobalt Studios West: 19 units due in 11 days (pretax budget cap $178,604)
- Ironside Conservatory: 23 units due in 11 days (pretax budget cap $209,660)
- Hartland Bureau: 21 units due in 11 days (pretax budget cap $191,095)
- Evergreen Boutique: 30 units due in 11 days (pretax budget cap $262,603)
- Stonewall Consortium: 22 units due in 12 days (pretax budget cap $198,822)
- Metro Outfitters: 23 units due in 12 days (pretax budget cap $203,901)
- Peak Fabricators: 23 units due in 12 days (pretax budget cap $206,743)
- Northbridge Academy: 23 units due in 12 days (pretax budget cap $205,801)
- Bayshore Trust: 18 units due in 12 days (pretax budget cap $166,220)
- Fairview Group: 20 units due in 13 days (pretax budget cap $182,900)
- Copper Collective: 26 units due in 13 days (pretax budget cap $224,876)

On-hand finished stock covers 203 units. If stock runs short, you can close the gap with finished-goods purchasing, in-house manufacturing, or a combination of the two.

Across all units covered through new purchasing or manufacturing, keep portfolio-level new-spend margin at or above 26.7% at selling price.

## Background & Policy

* The rules for which orders can be accepted are outlined below.
* Accepted orders must allow at least 10 days of lead time.
* Reject or cancel any order that fails those acceptance rules.
* Arrange supply for eligible orders, ensuring the least new investment.
* The combined units covered through new purchasing or manufacturing must clear at least 26.7% portfolio-level new-spend margin at selling price.
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
* Check Internal Notes/comments on stock, customers, vendors, and workcenters before you release anything.

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
