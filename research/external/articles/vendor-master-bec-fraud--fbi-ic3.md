# Business Email Compromise: The $55 Billion Scam

- **URL:** https://www.ic3.gov/PSA/2024/PSA240911
- **Publisher:** FBI Internet Crime Complaint Center (IC3)
- **Retrieved:** 2026-08-10
- **Topic:** vendor-master-bec-fraud

## Summary

This IC3 public service announcement is the FBI's periodic update on Business Email Compromise / Email Account Compromise (BEC/EAC) loss statistics, plus a short list of defensive practices for organizations that process transfer-of-funds requests.

### Definition and scope

IC3 defines BEC/EAC as a scam that targets both businesses and individuals who perform legitimate transfer-of-funds requests. The attacker compromises a legitimate email account through social engineering or computer intrusion, then either executes an unauthorized transfer of funds or extracts personally identifiable information that is used to compromise additional accounts. The announcement treats "BEC" and "EAC" as the same reporting category.

### Exposed-loss statistics (global, October 2013 – December 2023)

- **305,033** total incidents
- **$55,499,915,582** total exposed dollar loss

Broken out by victim location:

- **U.S. victims:** 158,436 victims / **$20,089,561,364** exposed loss
- **Non-U.S. victims:** 6,546 victims / **$1,638,490,375** exposed loss

### Where the money went (financial-recipient data, June 2016 – December 2023)

- **U.S.-based financial recipients:** 89,756 / **$17,499,104,054**
- **Non-U.S.-based financial recipients:** 22,190 / **$8,953,920,759**

### Geographic spread

BEC has been reported in **all 50 U.S. states and 186 countries**, with **more than 140 countries** receiving fraudulent transfers. IC3 names the **United Kingdom** and **Hong Kong** as the international banks most often acting as an intermediary stop for fraudulent funds, followed by **China, Mexico, and the United Arab Emirates**.

### Published self-protection steps

The PSA lists these defensive practices (summarized, order as published):

1. **Use secondary channels and two-factor authentication to verify requests for account information changes.** This is the control that maps directly to vendor bank-detail change fraud: the verification must occur on a channel other than the one that carried the request.
2. Use unique passwords and change them periodically.
3. Validate that the URL in an email is associated with the business/individual it claims to be from.
4. Look for hyperlinks that contain misspellings of the actual domain name.
5. Never supply login credentials or PII of any sort via email.
6. Verify the email address used to send email, especially when using a mobile device, by ensuring the sender address appears to match who it is coming from.
7. Ensure the settings on employees' computers are enabled to allow full email extensions to be viewed.
8. Monitor personal and business financial accounts routinely for irregularities such as missing deposits.

### Response guidance

If a fraudulent transfer is discovered, the PSA directs victims to **contact their financial institution immediately**, request that the institution **contact the receiving financial institution to attempt a recall of funds**, and obtain any **required indemnification documents**. Victims are directed to **file a complaint at ic3.gov immediately**, regardless of dollar amount.

### Explicit gap

The retrieved page text does **not** state a specific hour-count deadline (e.g., a 72-hour Financial Fraud Kill Chain window) or a minimum dollar threshold for recall requests — it says only "immediately." Do not assume a numeric reporting window from this source.

## Eval-relevant hooks

- An agent handling a vendor bank-detail change email must be scored on whether it verifies via a **secondary channel** rather than replying to the email or calling a number contained in it — this is IC3's own #1 listed control.
- Checkable assertion: cumulative global BEC exposed loss reported to IC3 for Oct 2013–Dec 2023 is **$55,499,915,582** across **305,033** incidents; U.S. victims account for **158,436** incidents and **$20,089,561,364**.
- Task hook: given a fraudulent wire that has just left the account, the correct first actions are (a) contact the originating financial institution to request a recall through the receiving institution, (b) obtain indemnification documents, (c) file an IC3 complaint — an agent that only emails the vendor fails.
- Red-flag detection task: the PSA's items 3, 4, 6, and 7 form a checkable list for inspecting a spoofed vendor email (URL/domain mismatch, misspelled domain, sender-address mismatch, truncated email extensions on mobile).
- Jurisdiction hook: fraudulent BEC transfers most often route through intermediary banks in the **UK and Hong Kong**, then China, Mexico, and the UAE — usable as a geographic risk-scoring rule for a payment-screening task.
