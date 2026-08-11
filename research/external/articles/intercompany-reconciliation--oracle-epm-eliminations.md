# Intercompany Eliminations (Oracle EPM Financial Consolidation and Close)

- **URL:** https://docs.oracle.com/en/cloud/saas/financial-consolidation-cloud/agfcc/intercompany_eliminations.html
- **Publisher:** Oracle (Administering Financial Consolidation and Close, Oracle Cloud EPM)
- **Retrieved:** 2026-08-10
- **Topic:** intercompany-reconciliation

## Summary

This is the administrator-level specification of how a consolidation engine actually posts intercompany elimination entries — the mechanics behind "it all nets out in consolidation." It is unusually concrete about the *shape* of an elimination journal entry, where the residual difference lands, and the ownership-percentage arithmetic that caps how much gets eliminated.

### Plug accounts

Every intercompany account must have a valid **Plug** (clearing) account assigned in its metadata. The plug account is where the difference between the two sides of an intercompany pair comes to rest once eliminations run. Posting behavior depends on how the plug account itself is flagged:

- If the Plug account is **not** set as an Intercompany account, the plug entry is posted to **`FCCS_No Intercompany`** in the Intercompany dimension.
- If the Plug account **is** set as an Intercompany account, it follows standard intercompany posting rules.

### The two-entry structure of every elimination

Each elimination consists of **exactly two offsetting entries**, both written to the **`FCCS_Intercompany Eliminations`** member of the Data Source dimension, inside the **`Elimination`** member of the Consolidation dimension:

1. **Reversal entry** — reverses (or partially reverses) the original intercompany amount.
2. **Plug entry** — posted to the Plug account named in the source intercompany account's metadata, offsetting entry 1 so debits equal credits.

Both entries inherit all dimension members from the source POV *except* the Consolidation dimension and the Data Source dimension.

### When data is a candidate for elimination

**Flat structure** — all three must hold:
1. The account is an intercompany account with a valid Plug account assigned.
2. The Intercompany dimension entry is not `FCCS_No Intercompany` (i.e., a valid partner is present).
3. Both entity and partner consolidate to the parent at **greater than 0%**.

**Multi-level structure** — all four must hold: conditions 1 and 2 above, plus (3) both entity and partner consolidate to a **common parent or ancestor at > 0%**, and (4) the **intercompany partner is a sibling of the current entity, or a descendant of a sibling**. Entity and partner need not consolidate to the immediate common parent; either or both may reach a common ancestor through intermediate parents.

### How much gets eliminated — the consolidation-percentage rule

In a flat structure the elimination amount is the **lower of the entity Consolidation % and the partner Consolidation %**. In a multi-level structure it is the **lower of the sums (across sibling entities/branches) of the cumulative entity Consolidation % and the cumulative partner Consolidation %**, where cumulative % is computed by multiplying the level-by-level percentages from the entity/partner up to the common ancestor.

Hard limits stated: the elimination amount **cannot exceed the proportionalized amount**; if either entity is proportionalized at less than 100%, only the **lowest proportional amount** is eliminated; if either entity's Consolidation % is **0%, no elimination is processed**; and once the net contribution is fully eliminated, no further eliminations occur.

### Precision and override settings

The engine applies **4-decimal precision by default**, and treats net contributions below **0.0001** as zero, blocking further elimination. This is configurable via a substitution variable named **`DecimalPrecision`** (Variables card → Substitution Variables tab), whose value must be an integer or subsequent consolidations fail: a positive integer rounds to that many decimals, zero rounds to integer, and a negative integer rounds to a multiple of 10 (e.g., -2 rounds to the nearest 100).

A second substitution variable, **`StrictElimCondition` = `False`**, disables the strict partner-relationship validation so entity–partner matches that would otherwise fail the sibling test will still eliminate.

## Eval-relevant hooks

- Checkable assertion: a correctly formed elimination is **two** entries (reversal + plug) in `FCCS_Intercompany Eliminations` under the `Elimination` consolidation member — an agent proposing a single-sided entry is wrong.
- Computation task: given entity and partner consolidation percentages in a multi-level hierarchy, compute the eliminated amount as the lower of the cumulative (multiplied level-by-level) percentages; a 0% side means no elimination at all.
- Diagnosis task: a residual balance sitting in a plug account is the expected home of an intercompany out-of-balance — an agent should read the plug balance as the unreconciled difference, not as an error in the consolidation.
- Configuration trap: rounding artifacts below 0.0001 are suppressed by the default 4-decimal precision; `DecimalPrecision` must be an integer or consolidation fails.
- Rule-application task: decide whether a given entity/partner pair is an elimination candidate by walking the 3-condition (flat) or 4-condition (multi-level, sibling/descendant-of-sibling) checklist.
- `StrictElimCondition = False` is a governance red flag an agent could be asked to spot in a configuration review.
