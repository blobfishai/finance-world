# AS 2315: Audit Sampling

- **URL:** https://pcaobus.org/oversight/standards/auditing-standards/details/AS2315
- **Publisher:** PCAOB (Public Company Accounting Oversight Board)
- **Retrieved:** 2026-08-10
- **Topic:** audit-pbc-evidence

## Summary

AS 2315 governs how much testing is enough and how sample results are projected. It is the source of the numeric machinery behind sample sizes, tolerable misstatement, and the "one exception blows the test" outcomes that drive PBC re-requests.

### Definition and approaches

Audit sampling is the application of an audit procedure to **less than 100 percent** of the items within an account balance or class of transactions (.01). The standard applies to both **nonstatistical and statistical** sampling (.03); both can produce sufficient evidence when properly applied (.03, .45). Statistical sampling adds the ability to design efficient samples, measure the sufficiency of evidence obtained, and **quantify sampling risk** (.46).

### The four risks (.12)

For **substantive tests of details**: the **risk of incorrect acceptance** (sample supports a conclusion that the balance is not materially misstated when it is) and the **risk of incorrect rejection** (the reverse). For **tests of controls**: the **risk of assessing control risk too low** and **too high**. Incorrect acceptance / assessing control risk too low relate to audit effectiveness; the other two relate to efficiency.

### Sample size drivers

**Substantive tests of details** (.18–.23A, Table 1): **tolerable misstatement** — the maximum monetary misstatement that could exist without causing material misstatement (.18); the **risk of incorrect acceptance**, itself a function of inherent risk, control risk, and the effectiveness of other substantive procedures (.19, .23); and the **expected size and frequency of misstatements** in the population (.23). Lower assessed inherent risk, lower assessed control risk, and more effective analytical/other substantive procedures each permit a **smaller** sample.

**Tests of controls** (.31–.38): the **tolerable rate of deviation** — the maximum deviation rate that would still support the planned assessed level of control risk (.34); the **expected deviation rate** (.38); the **allowable risk of assessing control risk too low** (.31, .37); and population characteristics.

**Stratification** (.22): sample size can be reduced by separating the population into relatively homogeneous groups on a characteristic related to the audit objective — recorded/book value, the nature of controls over processing, or special considerations attaching to certain items.

**Items examined 100%** (.21): the auditor should examine items for which accepting any sampling risk is not justified — for example, items whose potential misstatement could individually **equal or exceed tolerable misstatement**.

### Projection — with the standard's own numbers

Paragraph .26 gives the projection mechanic: a sample of **50 items from a population of 1,000** in which **$3,000** of overstatement is found projects to a **$60,000** overstatement — the sample misstatement divided by the fraction of the population sampled ($3,000 ÷ 50/1,000). Projected misstatement must be added to misstatements in the 100%-examined items and compared to tolerable misstatement, with sampling risk considered.

Worked threshold example (.26): with an account balance of **$1 million** and tolerable misstatement of **$50,000**, a total projected misstatement of **$10,000** may support reasonable assurance of acceptably low sampling risk; if projected misstatement is **close to** tolerable misstatement, the risk that actual misstatement exceeds tolerable is unacceptably high.

Controls example (.41): if the **tolerable rate is 5 percent** and **no deviations** are found in a sample of **60 items**, sampling risk that the true rate exceeds 5 percent may be acceptably low; if the sample contains **two or more deviations**, that risk is unacceptably high.

### Evaluating results

Qualitative evaluation (.27) requires considering the nature and cause of misstatements — **error versus fraud**, differences in principle versus application, and the relationship to other phases of the audit; fraud demands broader consideration. If discovered misstatements exceed the expected frequency or amount, the auditor should reconsider the planning assumptions and risk assessments and may need to modify other tests (.28).

**Unexamined items** (.25): where documentation for a selected item cannot be located, if treating those items as misstated would lead to a conclusion of material misstatement, the auditor should consider alternative procedures that provide sufficient evidence; the auditor must also weigh implications for risk assessment, questions about management/employee integrity, and effects on other aspects of the audit.

### Selection and dual-purpose samples

Every item in the population must have an opportunity to be selected; haphazard and random-based selection are named examples (.24). For tests of controls, the selection method must have the potential to select items **from the entire period under audit** (.39). A **dual-purpose sample** must be the **larger** of the two samples that would otherwise have been designed, and deviations and monetary misstatements are evaluated **separately** at their respective risk levels (.44).

### The risk model (Appendix)

**AR = IR × CR × AP × TD**, rearranged as **TD = AR / (IR × CR × AP)**, where AR is allowable audit risk, IR inherent risk, CR control risk, AP the risk that analytical procedures/other relevant substantive tests fail to detect a misstatement, and TD the risk of incorrect acceptance. Table 2 examples at **AR = 5%, IR = 100%**: CR 10% / AP 30% → **TD = 16.7%**; CR 30% / AP 50% → **TD = 3.3%**; CR 50% / AP 50% → **TD = 2%**; CR 100% / AP 100% → **TD = 5%**.

Effective for periods ended on or after **June 25, 1983**; amendments to paragraph .11 effective **December 15, 2026**.

## Eval-relevant hooks

- Projection computation task: sample of 50 from 1,000 with $3,000 found → $60,000 projected; then compare against tolerable misstatement to conclude pass/fail. Fully checkable arithmetic.
- Threshold decision rule: tolerable misstatement $50,000 against a $1M balance — projected $10,000 is acceptable; projected "close to" $50,000 is not.
- Controls-testing rule: tolerable rate 5%, sample of 60, zero deviations → acceptable; two or more deviations → unacceptable. A clean pass/fail gate for a control test task.
- Risk-model computation: TD = AR / (IR × CR × AP), with the published table values (16.7% / 3.3% / 2% / 5%) as verifiable answers.
- Scoping rule: items whose potential misstatement individually equals or exceeds tolerable misstatement must be examined 100% and excluded from the sampled population.
- Dual-purpose rule: sample size is the larger of the two designs, and the two evaluations are performed separately — a frequent shortcut error.
- Missing-document handling: an unlocatable item is not simply dropped; the auditor must consider treating it as misstated and perform alternative procedures — this is the standard-backed reason a PBC item cannot be waived.
