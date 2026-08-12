#!/usr/bin/env python3
"""Clone microsoft/FinanceBenchmark erp_qa questions into working finance-world tasks.

Each generated task keeps the benchmark's question **verbatim** (that's the clone) but its
ground truth is **recomputed in-world** from core.sqlite — never copied from the benchmark's
prose, which does not reconcile with its own shipped data (docs/AUDIT.md A3). Grading is
deterministic field checks instead of the benchmark's LLM judge.

Routing: FB's `scenario` label is coarse — "Aged Balance" carries bucket questions, due-window
questions, plain-balance questions and one "give me the customer's details"; "Vendors" carries
discounts, hold status and payment terms. So a scenario does not name a handler, it names a
LIST of routes, and a question is only cloned if some route's wording matches IT. A question
that matches no route is rejected (printed with the reason) rather than pushed through the
nearest handler, because a mis-route produces a task whose graded fields do not answer its own
prompt — prompt/verifier drift the S4 field-name check cannot see.

Three honest edge cases, all of them real:
  * the named customer/vendor is not in this world's master data (Sunset Wholesales, Ade
    Supply Company, Yellow Square, "Contoso Retail San Diego" — where a *shorter* neighbour
    "Contoso Retail" does exist). Those clone as empty-answer traps (none_answer) carrying a
    re-derivable COUNT(*)=0, which is what the question is really worth in this world.
  * the question asks about a period before this ledger begins ("payments in 2017"). Same
    treatment: a real hallucination trap, not a skip.
  * the question contains a literal placeholder ("in yyyy") or asks for an attribute this
    world does not model (vendor creation date, an unposted-invoice register). Those are
    excluded and printed with the reason.

Usage: python3 world/etl/clone_fb_erp.py [--per-scenario N] [--out tasks/erp_qa_fb]
"""
import argparse, datetime as dt, json, re, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "world/build/core.sqlite"
DATASET = ROOT / "research/external/financebenchmark-extracts/data/dataset.yaml"
EPOCH = "2026-03-02"
E = dt.date.fromisoformat(EPOCH)

def slug(s, n=48):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")[:n]

def qq(s):
    return str(s).replace("'", "''")

def in_list(vals):
    return "(" + ",".join("'" + qq(v) + "'" for v in vals) + ")"

def one(cx, sql, args=()):
    r = cx.execute(sql, args).fetchone()
    return r[0] if r and r[0] is not None else 0

def r2(v):
    return round(v or 0, 2)

def sqlstep(sql):
    return ("data_find_entities_sql", {"sql": sql})

# ------------------------------------------------------------------ resolution
_STOP = {"what", "whats", "what's", "which", "who", "when", "where", "how", "is", "are", "do",
         "does", "did", "show", "provide", "list", "could", "can", "of", "the", "in", "as",
         "for", "base", "reply", "total", "usmf", "erp", "ap", "ar", "us", "eur", "usd",
         "march", "january", "february", "april", "group", "net", "status", "customer",
         "customers", "vendor", "vendors", "please", "give", "me", "all", "and", "premium"}
_PHRASE = re.compile(r"\b([A-Z][\w&.'\-]*(?:\s+[A-Z][\w&.'\-]*)+)")
_ACCT = re.compile(r"\b(SYN(?:CUS|VEN)-\d{4}|US-\d{3}|DE-\d{3}|\b1001\b|\b1002\b)")

def _norm(s):
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())

def _phrases(query):
    """Capitalised multi-word phrases in the question — the entities it names."""
    out = []
    for m in _PHRASE.finditer(query):
        toks = m.group(1).split()
        while toks and toks[0].lower().strip(".,'") in _STOP:
            toks.pop(0)
        while toks and (toks[-1].lower().strip(".,'") in _STOP
                        or re.fullmatch(r"(?:US|DE|SYNCUS|SYNVEN)-\d+", toks[-1], re.I)):
            toks.pop()
        if len(toks) >= 2:
            out.append(" ".join(toks))
    return out

def _named(cx, phrase):
    """Master-data rows whose name contains this phrase (separator-insensitive)."""
    n = _norm(phrase)
    hits = []
    for tbl in ("erp_customers", "erp_vendors"):
        for acct, name in cx.execute(f"SELECT account, name FROM {tbl}"):
            if name and n in _norm(name):
                hits.append((acct, name, tbl))
    return hits

def resolve(cx, query, segment):
    """(accounts, name, side, missing).

    An explicit account id wins. Otherwise the longest master-data name that appears in the
    text wins, and EVERY account carrying that name is returned — 301 customer names in this
    world are shared by more than one account, and grading one of them while the question
    names all of them is the same drift the route gate exists to prevent.

    `missing` is set when the question clearly names an entity that master data does not
    have (including the case where the question's phrase merely *starts* with a real name:
    "Contoso Retail San Diego" is not "Contoso Retail")."""
    m = _ACCT.search(query)
    if m:
        for tbl, side in (("erp_customers", "cust"), ("erp_vendors", "vend")):
            r = cx.execute(f"SELECT account, name FROM {tbl} WHERE account=?", (m.group(1),)).fetchone()
            if r: return [r[0]], r[1], side, None

    nq = _norm(query)
    best = None
    order = (("erp_vendors", "vend"), ("erp_customers", "cust")) if segment == "AP" \
            else (("erp_customers", "cust"), ("erp_vendors", "vend"))
    for tbl, side in order:
        for acct, name in cx.execute(f"SELECT account, name FROM {tbl}").fetchall():
            if not name or len(name) <= 4: continue
            n = _norm(name)
            hit = n in nq or (len(n) >= 10 and n.endswith("s") and n[:-1] in nq)
            if hit and (not best or len(n) > len(best[3])):
                best = (acct, name, side, n, tbl)

    phrases = _phrases(query)
    if best:
        # the question may name a LONGER entity than the one we matched.
        over = [p for p in phrases
                if _norm(p).startswith(best[3]) and len(_norm(p)) > len(best[3]) and not _named(cx, p)]
        if over:
            return [], None, ("vend" if segment == "AP" else "cust"), max(over, key=len)
        accts = [a for (a,) in cx.execute(f"SELECT account FROM {best[4]} WHERE name=?", (best[1],))]
        return accts, best[1], best[2], None

    absent = [p for p in phrases if not _named(cx, p)]
    if absent:
        return [], None, ("vend" if segment == "AP" else "cust"), max(absent, key=len)
    return [], None, None, None

class Ctx:
    def __init__(self, cx, q, seg, accts, name, side, missing):
        self.cx, self.q, self.seg = cx, q, seg
        self.accts, self.name, self.missing = accts, name, missing
        self.side = side or ("vend" if seg == "AP" else "cust")
        self.acct = accts[0] if accts else None
        self.IN = f"account IN {in_list(accts)}" if accts else "1=0"
        self.table = "erp_vendors" if self.side == "vend" else "erp_customers"
        self.trans = "erp_vend_trans" if self.side == "vend" else "erp_cust_trans"

def days_arg(q, default=7):
    m = re.search(r"next (\d+) days", q, re.I)
    return int(m.group(1)) if m else default

def date_arg(q, default=EPOCH):
    m = re.search(r"(january|february|march|april|may|june|july|august|september|october|"
                  r"november|december)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", q, re.I)
    if not m: return default
    mon = ["january", "february", "march", "april", "may", "june", "july", "august",
           "september", "october", "november", "december"].index(m.group(1).lower()) + 1
    return dt.date(int(m.group(3)), mon, int(m.group(2))).isoformat()

def none_field(what):
    return (f"none - {what}", "none")

# ================================ handlers ==================================
# Each returns (fields, walk_steps[, gt_sql_by_field]).
# field kinds: number | contains | all (list) | none (none_answer) | yes_no | string

def h_absent(cx, C, answer_field, count_field):
    """The question names an entity this world's master data does not have."""
    tbl, what = C.table, ("vendor" if C.side == "vend" else "customer")
    like = "%" + qq(C.missing.lower()) + "%"
    sql = f"SELECT COUNT(*) FROM {tbl} WHERE LOWER(name) LIKE '{like}'"
    n = one(cx, sql)
    if n: return None                       # not actually missing — never fake a trap
    return ({count_field: (0, "number"),
             answer_field: none_field(f"no {what} named '{C.missing}' exists in USMF")},
            [("data_find_entities", {"entity": "Vendors" if C.side == "vend" else "Customers",
                                     "filters": {"name": C.missing}})],
            {count_field: sql})

# --- credit -----------------------------------------------------------------
def h_credit_limit(cx, C):
    v = one(cx, f"SELECT credit_max FROM erp_customers WHERE account='{qq(C.acct)}'")
    return ({"credit_limit": (v, "number"), "customer_account": (C.acct, "contains")},
            [("data_find_entities", {"entity": "Customers", "filters": {"account": C.acct}})],
            {"credit_limit": f"SELECT credit_max FROM erp_customers WHERE account='{qq(C.acct)}'"})

def h_credit_available(cx, C):
    lim = one(cx, f"SELECT credit_max FROM erp_customers WHERE account='{qq(C.acct)}'")
    bal_sql = (f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans "
               f"WHERE {C.IN} AND closed=0")
    bal = one(cx, bal_sql)
    return ({"credit_limit": (lim, "number"),
             "open_balance": (r2(bal), "number"),
             "available_credit": (r2(lim - bal), "number")},
            [("data_find_entities", {"entity": "Customers", "filters": {"account": C.acct}}),
             sqlstep(bal_sql)],
            {"credit_limit": f"SELECT credit_max FROM erp_customers WHERE account='{qq(C.acct)}'",
             "open_balance": bal_sql})

def h_credit_utilisation(cx, C):
    lim = one(cx, f"SELECT credit_max FROM erp_customers WHERE account='{qq(C.acct)}'")
    bal_sql = (f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans "
               f"WHERE {C.IN} AND closed=0")
    bal = one(cx, bal_sql)
    if not lim: return None
    return ({"credit_limit": (lim, "number"), "open_balance": (r2(bal), "number"),
             "credit_utilisation_pct": (round(bal / lim * 100, 2), "number")},
            [("data_find_entities", {"entity": "Customers", "filters": {"account": C.acct}}),
             sqlstep(bal_sql)],
            {"credit_limit": f"SELECT credit_max FROM erp_customers WHERE account='{qq(C.acct)}'",
             "open_balance": bal_sql})

def h_credit_hold(cx, C):
    sql = ("SELECT COUNT(*) FROM erp_customers "
           "WHERE COALESCE(LOWER(on_hold),'open') NOT IN ('open','no','none')")
    n = one(cx, sql)
    pop = "SELECT COUNT(*) FROM erp_customers"
    f = {"customers_on_credit_hold": (n, "number"), "customers_reviewed": (one(cx, pop), "number")}
    f["customer_accounts"] = none_field("no customer in USMF is on credit hold") if not n else \
        (", ".join(a for (a,) in cx.execute(
            "SELECT account FROM erp_customers WHERE COALESCE(LOWER(on_hold),'open') "
            "NOT IN ('open','no','none') LIMIT 10")), "contains")
    return (f, [sqlstep("SELECT account, name, on_hold FROM erp_customers WHERE on_hold IS NOT NULL "
                        "AND LOWER(on_hold) NOT IN ('open','no') LIMIT 25"),
                sqlstep("SELECT on_hold, COUNT(*) AS customers FROM erp_customers GROUP BY on_hold")],
            {"customers_on_credit_hold": sql, "customers_reviewed": pop})

def h_over_credit_limit(cx, C):
    grp = re.search(r"group (\d+)", C.q, re.I)
    topn = int((re.search(r"top (\d+)", C.q, re.I) or [0, 10])[1]) if re.search(r"top (\d+)", C.q, re.I) else 10
    where = "t.txn_type='Invoice' AND t.closed=0" + (f" AND c.customer_group='{grp.group(1)}'" if grp else "")
    sql = (f"SELECT t.account, c.name, ROUND(SUM(t.amount-t.settled)-c.credit_max,2) AS over_limit "
           f"FROM erp_cust_trans t JOIN erp_customers c ON c.account=t.account WHERE {where} "
           f"GROUP BY t.account HAVING SUM(t.amount-t.settled) > c.credit_max "
           f"ORDER BY over_limit DESC LIMIT {topn}")
    rows = cx.execute(sql).fetchall()
    if not rows: return None
    top = rows[0]
    gt = (f"SELECT ROUND(COALESCE(SUM(amount-settled),0) - "
          f"(SELECT credit_max FROM erp_customers WHERE account='{qq(top[0])}'),2) "
          f"FROM erp_cust_trans WHERE account='{qq(top[0])}' AND txn_type='Invoice' AND closed=0")
    return ({"customers_listed": (len(rows), "number"),
             "top_customer_account": (top[0], "contains"),
             "top_customer_over_limit_amount": (r2(top[2]), "number")},
            [sqlstep(sql)], {"top_customer_over_limit_amount": gt})

def h_credit_rating(cx, C):
    v = cx.execute(f"SELECT credit_rating FROM erp_customers WHERE account='{qq(C.acct)}'").fetchone()[0]
    return ({"credit_rating": (v, "contains"), "customer_account": (C.acct, "contains")},
            [("data_find_entities", {"entity": "Customers", "filters": {"account": C.acct}})])

# --- customer master --------------------------------------------------------
def h_customer_setup(cx, C):
    v = cx.execute(f"SELECT payment_term FROM erp_customers WHERE account='{qq(C.acct)}'").fetchone()[0]
    return ({"payment_terms": (v, "contains"), "customer_account": (C.acct, "contains")},
            [("data_find_entities", {"entity": "Customers", "filters": {"account": C.acct}}),
             ("data_find_entities", {"entity": "PaymentTerms", "filters": {"code": v}})])

def h_phone(cx, C):
    rows = cx.execute(f"SELECT account, phone FROM erp_customers WHERE {C.IN} ORDER BY account").fetchall()
    if not rows or not rows[0][1]: return None
    step = [("data_find_entities", {"entity": "Customers", "filters": {"name": C.name}})]
    if len(rows) == 1:
        return ({"phone_number": (rows[0][1], "contains"), "customer_account": (rows[0][0], "contains")}, step)
    # the name is carried by several accounts: the honest answer names all of them
    return ({"matching_customer_count": (len(rows), "number"),
             "phone_numbers": ([r[1] for r in rows], "all")}, step,
            {"matching_customer_count": f"SELECT COUNT(*) FROM erp_customers WHERE name='{qq(C.name)}'"})

def h_contact(cx, C):
    rows = cx.execute(f"SELECT account, contact_name, contact_email, phone FROM erp_customers "
                      f"WHERE {C.IN} ORDER BY account").fetchall()
    if not rows: return None
    step = [("data_find_entities", {"entity": "Customers", "filters": {"name": C.name}})]
    if len(rows) == 1:
        a, cn, em, ph = rows[0]
        return ({"contact_name": (cn, "contains"), "contact_email": (em, "contains"),
                 "phone_number": (ph, "contains")}, step)
    return ({"matching_customer_count": (len(rows), "number"),
             "contact_emails": ([r[2] for r in rows], "all")}, step,
            {"matching_customer_count": f"SELECT COUNT(*) FROM erp_customers WHERE name='{qq(C.name)}'"})

def h_customer_details(cx, C):
    r = cx.execute(f"SELECT account, customer_group, payment_term, credit_max FROM erp_customers "
                   f"WHERE account='{qq(C.acct)}'").fetchone()
    bal_sql = f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans WHERE {C.IN} AND closed=0"
    return ({"customer_account": (r[0], "contains"), "customer_group": (r[1], "contains"),
             "credit_limit": (r[3], "number"), "open_balance": (r2(one(cx, bal_sql)), "number")},
            [("data_find_entities", {"entity": "Customers", "filters": {"name": C.name}}),
             sqlstep(bal_sql)],
            {"credit_limit": f"SELECT credit_max FROM erp_customers WHERE account='{qq(r[0])}'",
             "open_balance": bal_sql})

def h_customers_in_group(cx, C):
    m = re.search(r"group (\d+)", C.q, re.I)
    if not m: return None
    g = m.group(1)
    sql = f"SELECT COUNT(*) FROM erp_customers WHERE customer_group='{g}'"
    return ({"customer_count": (one(cx, sql), "number"), "customer_group": (g, "contains")},
            [sqlstep(f"SELECT customer_group, COUNT(*) AS customers FROM erp_customers GROUP BY customer_group"),
             sqlstep(f"SELECT account, name FROM erp_customers WHERE customer_group='{g}' LIMIT 25")],
            {"customer_count": sql})

def h_customers_by_currency(cx, C):
    m = re.search(r"\b(EUR|USD|GBP|CHF)\b", C.q)
    if not m: return None
    ccy = m.group(1)
    sql = f"SELECT COUNT(*) FROM erp_customers WHERE currency='{ccy}'"
    n = one(cx, sql)
    f = {"customer_count": (n, "number")}
    if 0 < n <= 5:
        f["customer_accounts"] = ([a for (a,) in cx.execute(
            f"SELECT account FROM erp_customers WHERE currency='{ccy}' ORDER BY account")], "all")
    return (f, [sqlstep("SELECT currency, COUNT(*) AS customers FROM erp_customers GROUP BY currency"),
                sqlstep(f"SELECT account, name, currency FROM erp_customers WHERE currency='{ccy}' LIMIT 25")],
            {"customer_count": sql})

# --- AR balances ------------------------------------------------------------
def h_outstanding(cx, C):
    w = f"{C.IN} AND txn_type='Invoice' AND closed=0"
    n = one(cx, f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}")
    t = r2(one(cx, f"SELECT SUM(amount-settled) FROM erp_cust_trans WHERE {w}"))
    f = {"unpaid_invoice_count": (n, "number")}
    f["unpaid_total"] = (t, "number") if n else none_field("no unpaid invoices are open for this customer")
    return (f, [sqlstep(f"SELECT invoice, due_date, ROUND(amount-settled,2) AS open FROM erp_cust_trans WHERE {w}")],
            {"unpaid_invoice_count": f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}",
             **({"unpaid_total": f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans WHERE {w}"} if n else {})})

def h_customer_balance(cx, C):
    w = f"{C.IN} AND txn_type='Invoice' AND closed=0"
    n = one(cx, f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}")
    t = r2(one(cx, f"SELECT SUM(amount-settled) FROM erp_cust_trans WHERE {w}"))
    f = {"open_invoice_count": (n, "number")}
    f["open_balance"] = (t, "number") if n else none_field("this customer has no open receivables")
    return (f, [sqlstep(f"SELECT invoice, due_date, ROUND(amount-settled,2) AS open FROM erp_cust_trans WHERE {w}")],
            {"open_invoice_count": f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}",
             **({"open_balance": f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans WHERE {w}"} if n else {})})

def h_aged_buckets(cx, C):
    rows = cx.execute(f"""SELECT due_date, amount-settled FROM erp_cust_trans
                          WHERE {C.IN} AND txn_type='Invoice' AND closed=0""").fetchall()
    if not rows:
        cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {C.IN} AND txn_type='Invoice' AND closed=0"
        return ({"open_invoice_count": (0, "number"),
                 "aged_balance": none_field("this customer has no open receivables, so every "
                                            "aging bucket is empty")},
                [sqlstep(f"SELECT invoice, due_date, closed, ROUND(amount-settled,2) AS open "
                         f"FROM erp_cust_trans WHERE {C.IN}")], {"open_invoice_count": cnt})
    b = {"not_due": 0.0, "b1_30": 0.0, "b31_60": 0.0, "b61_90": 0.0, "b90_plus": 0.0}
    for due, open_amt in rows:
        d = (E - dt.date.fromisoformat(due)).days
        k = "not_due" if d <= 0 else "b1_30" if d <= 30 else "b31_60" if d <= 60 \
            else "b61_90" if d <= 90 else "b90_plus"
        b[k] = round(b[k] + open_amt, 2)
    past_due = round(b["b1_30"] + b["b31_60"] + b["b61_90"] + b["b90_plus"], 2)
    gt = (f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans WHERE {C.IN} "
          f"AND txn_type='Invoice' AND closed=0 AND julianday('{EPOCH}') - julianday(due_date) > 0")
    return ({"total_past_due": (past_due, "number"),
             "not_yet_due": (round(b["not_due"], 2), "number"),
             "over_90_days": (b["b90_plus"], "number")},
            [("api_find_actions", {"query": "aged balances"}),
             ("api_invoke_action", {"action": "ContosoCustAgedBalancesLive",
                                    "parameters": {"customer_account": C.acct}})],
            {"total_past_due": gt})

def h_aged_topn(cx, C):
    grp = re.search(r"group (\d+)", C.q, re.I)
    topn = int((re.search(r"top (\d+)", C.q, re.I) or [0, 10])[1]) if re.search(r"top (\d+)", C.q, re.I) else 10
    by_open = "outstanding" in C.q.lower()
    where = "t.txn_type='Invoice' AND t.closed=0"
    if grp: where += f" AND c.customer_group='{grp.group(1)}'"
    if not by_open:
        where += (f" AND julianday('{EPOCH}') - julianday(t.due_date) > 90" if "90" in C.q
                  else f" AND t.due_date < '{EPOCH}'")
    metric = "balance" if by_open else "past_due"
    sql = (f"SELECT t.account, c.name, ROUND(SUM(t.amount-t.settled),2) AS {metric} "
           f"FROM erp_cust_trans t JOIN erp_customers c ON c.account=t.account WHERE {where} "
           f"GROUP BY t.account ORDER BY {metric} DESC LIMIT {topn}")
    rows = cx.execute(sql).fetchall()
    if not rows: return None
    field = "top_customer_outstanding" if by_open else "top_customer_past_due"
    gt = (f"SELECT ROUND(COALESCE(SUM(t.amount-t.settled),0),2) FROM erp_cust_trans t "
          f"JOIN erp_customers c ON c.account=t.account "
          f"WHERE {where} AND t.account='{qq(rows[0][0])}'")
    return ({"customers_listed": (len(rows), "number"),
             "top_customer_account": (rows[0][0], "contains"),
             field: (r2(rows[0][2]), "number")},
            [sqlstep(sql)], {field: gt})

def _bucket_case(lo, hi):
    d = f"julianday('{EPOCH}') - julianday(due_date)"
    cond = f"{d} <= 0" if hi == 0 else (f"{d} > {lo}" + (f" AND {d} <= {hi}" if hi else ""))
    return (f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans "
            f"WHERE txn_type='Invoice' AND closed=0 AND {cond}")

def h_aging_all_buckets(cx, C):
    spec = [("current_not_due", 0, 0), ("days_1_30", 0, 30), ("days_31_60", 30, 60),
            ("days_61_90", 60, 90), ("days_over_90", 90, None)]
    fields, sqls = {}, {}
    for name, lo, hi in spec:
        s = _bucket_case(lo, hi)
        fields[name] = (r2(one(cx, s)), "number"); sqls[name] = s
    return (fields, [("api_find_actions", {"query": "aged balances"}),
                     sqlstep(_bucket_case(90, None))], sqls)

def h_aged_180(cx, C):
    w = (f"txn_type='Invoice' AND closed=0 AND julianday('{EPOCH}') - julianday(due_date) > 180")
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans WHERE {w}"
    return ({"invoice_count": (one(cx, cnt), "number"),
             "past_due_180_plus_total": (r2(one(cx, tot)), "number")},
            [sqlstep(f"SELECT account, invoice, due_date, ROUND(amount-settled,2) AS open "
                     f"FROM erp_cust_trans WHERE {w} LIMIT 25"), sqlstep(tot)],
            {"invoice_count": cnt, "past_due_180_plus_total": tot})

def h_due_window(cx, C):
    d = days_arg(C.q, 7)
    end = (E + dt.timedelta(days=d - 1)).isoformat()
    w = (f"{C.IN} AND txn_type='Invoice' AND closed=0 AND due_date BETWEEN '{EPOCH}' AND '{end}'")
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"transactions_coming_due_count": (n, "number")}
    f["amount_coming_due"] = (r2(one(cx, tot)), "number") if n else \
        none_field(f"no open transaction for this customer falls due between {EPOCH} and {end}")
    return (f, [sqlstep(f"SELECT invoice, due_date, ROUND(amount-settled,2) AS open "
                        f"FROM erp_cust_trans WHERE {C.IN} AND closed=0")],
            {"transactions_coming_due_count": cnt, **({"amount_coming_due": tot} if n else {})})

# --- AR history -------------------------------------------------------------
def h_payment_history(cx, C):
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {C.IN} AND txn_type='Payment'"
    n = one(cx, cnt)
    step = [sqlstep(f"SELECT voucher, trans_date, ROUND(-amount,2) AS paid FROM erp_cust_trans "
                    f"WHERE {C.IN} AND txn_type='Payment' ORDER BY paid DESC")]
    if not n:
        return ({"payment_count": (0, "number"),
                 "payments": none_field("this customer has no payments in the AR subledger")},
                step, {"payment_count": cnt})
    r = cx.execute(f"""SELECT voucher, trans_date, ROUND(-amount,2) FROM erp_cust_trans
                       WHERE {C.IN} AND txn_type='Payment' ORDER BY -amount DESC LIMIT 1""").fetchone()
    return ({"payment_count": (n, "number"), "largest_payment_amount": (r[2], "number"),
             "largest_payment_voucher": (r[0], "contains"), "largest_payment_date": (r[1], "contains")},
            step, {"payment_count": cnt,
                   "largest_payment_amount": f"SELECT ROUND(MAX(-amount),2) FROM erp_cust_trans "
                                             f"WHERE {C.IN} AND txn_type='Payment'"})

def h_payments_in_year(cx, C):
    y = re.search(r"\b(19\d\d|20[0-2]\d)\b", C.q)
    year = y.group(1)
    w = f"{C.IN} AND txn_type='Payment' AND trans_date LIKE '{year}-%'"
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"payment_count": (n, "number")}
    f["payments"] = none_field(f"the AR subledger holds no payment for this customer in {year}") \
        if not n else (f"{n} payments in {year}", "contains")
    return (f, [sqlstep(f"SELECT MIN(trans_date) AS earliest, MAX(trans_date) AS latest "
                        f"FROM erp_cust_trans WHERE {C.IN}"),
                sqlstep(f"SELECT voucher, trans_date FROM erp_cust_trans WHERE {w}")],
            {"payment_count": cnt})

def h_invoicing_history(cx, C):
    w = f"{C.IN} AND txn_type='Invoice'"
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount),0),2) FROM erp_cust_trans WHERE {w}"
    return ({"invoice_count": (one(cx, cnt), "number"), "invoiced_total": (r2(one(cx, tot)), "number")},
            [sqlstep(f"SELECT invoice, trans_date, ROUND(amount,2) AS amount FROM erp_cust_trans WHERE {w}")],
            {"invoice_count": cnt, "invoiced_total": tot})

def h_positive_txns(cx, C):
    w = f"{C.IN} AND amount > 0"
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount),0),2) FROM erp_cust_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"positive_transaction_count": (n, "number")}
    f["positive_transaction_total"] = (r2(one(cx, tot)), "number") if n else \
        none_field("this customer has no positive transactions in the AR subledger")
    return (f, [sqlstep(f"SELECT txn_type, invoice, ROUND(amount,2) AS amount FROM erp_cust_trans "
                        f"WHERE {C.IN} ORDER BY amount DESC")],
            {"positive_transaction_count": cnt, **({"positive_transaction_total": tot} if n else {})})

def h_largest_invoice(cx, C):
    r = cx.execute("SELECT invoice, account, ROUND(amount,2) FROM erp_cust_trans "
                   "WHERE txn_type='Invoice' ORDER BY amount DESC LIMIT 1").fetchone()
    return ({"invoice_number": (r[0], "contains"), "customer_account": (r[1], "contains"),
             "invoice_amount": (r[2], "number")},
            [sqlstep("SELECT invoice, account, ROUND(amount,2) AS amount FROM erp_cust_trans "
                     "WHERE txn_type='Invoice' ORDER BY amount DESC LIMIT 10")],
            {"invoice_amount": "SELECT ROUND(MAX(amount),2) FROM erp_cust_trans WHERE txn_type='Invoice'"})

def h_top_invoiced_customer(cx, C):
    r = cx.execute("SELECT account, ROUND(SUM(amount),2) AS invoiced FROM erp_cust_trans "
                   "WHERE txn_type='Invoice' GROUP BY account ORDER BY invoiced DESC LIMIT 1").fetchone()
    return ({"customer_account": (r[0], "contains"), "total_invoiced": (r[1], "number")},
            [sqlstep("SELECT account, ROUND(SUM(amount),2) AS invoiced FROM erp_cust_trans "
                     "WHERE txn_type='Invoice' GROUP BY account ORDER BY invoiced DESC LIMIT 10")],
            {"total_invoiced": f"SELECT ROUND(COALESCE(SUM(amount),0),2) FROM erp_cust_trans "
                               f"WHERE txn_type='Invoice' AND account='{qq(r[0])}'"})

def h_cash_collections(cx, C):
    w = f"{C.IN} AND txn_type='Payment' AND trans_date >= '{EPOCH[:4]}-01-01'"
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(-amount),0),2) FROM erp_cust_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"payment_count_fy": (n, "number")}
    f["total_collected_fy"] = (r2(one(cx, tot)), "number") if n else \
        none_field(f"no cash was collected from this customer since {EPOCH[:4]}-01-01")
    return (f, [sqlstep(f"SELECT voucher, trans_date, ROUND(-amount,2) AS received "
                        f"FROM erp_cust_trans WHERE {w}")],
            {"payment_count_fy": cnt, **({"total_collected_fy": tot} if n else {})})

def h_credit_notes(cx, C):
    w = f"{C.IN} AND txn_type='CreditNote' AND closed=0"
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(-amount),0),2) FROM erp_cust_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"unapplied_credit_note_count": (n, "number")}
    f["unapplied_credit_total"] = (r2(one(cx, tot)), "number") if n else \
        none_field("this customer has no unapplied credit notes")
    return (f, [sqlstep(f"SELECT invoice, trans_date, ROUND(-amount,2) AS credit "
                        f"FROM erp_cust_trans WHERE {w}")],
            {"unapplied_credit_note_count": cnt, **({"unapplied_credit_total": tot} if n else {})})

def h_dispute(cx, C):
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {C.IN} AND disputed=1"
    return ({"disputed_transaction_count": (one(cx, cnt), "number")},
            [sqlstep(f"SELECT invoice, ROUND(amount,2) AS amount FROM erp_cust_trans "
                     f"WHERE {C.IN} AND disputed=1")], {"disputed_transaction_count": cnt})

def h_deductions(cx, C):
    w = f"{C.IN} AND deduction=1 AND closed=0"
    cnt = f"SELECT COUNT(*) FROM erp_cust_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(-amount),0),2) FROM erp_cust_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"open_deduction_count": (n, "number")}
    f["open_deduction_total"] = (r2(one(cx, tot)), "number") if n else \
        none_field("this customer has no open deductions")
    return (f, [sqlstep(f"SELECT invoice, ROUND(-amount,2) AS deduction FROM erp_cust_trans WHERE {w}")],
            {"open_deduction_count": cnt, **({"open_deduction_total": tot} if n else {})})

# --- cash discounts ---------------------------------------------------------
def h_cash_discounts(cx, C):
    cnt = (f"SELECT COUNT(*) FROM erp_settlements WHERE side='AR' AND {C.IN} AND cash_disc_taken > 0")
    return ({"discount_payment_count": (one(cx, cnt), "number")},
            [sqlstep(f"SELECT settle_date, ROUND(amount,2) AS settled, ROUND(cash_disc_taken,2) AS discount "
                     f"FROM erp_settlements WHERE side='AR' AND {C.IN}")],
            {"discount_payment_count": cnt})

def h_cust_disc_terms(cx, C):
    master = cx.execute(f"SELECT cash_disc_code FROM erp_customers WHERE account='{qq(C.acct)}'").fetchone()[0]
    cnt = (f"SELECT COUNT(*) FROM erp_cust_trans WHERE {C.IN} AND txn_type='Invoice' AND closed=0 "
           f"AND cash_disc_code IS NOT NULL")
    n = one(cx, cnt)
    return ({"has_active_cash_discount": ("yes" if (n or master) else "no", "yes_no"),
             "discounted_open_invoice_count": (n, "number")},
            [("data_find_entities", {"entity": "Customers", "filters": {"account": C.acct}}),
             sqlstep(f"SELECT invoice, cash_disc_code FROM erp_cust_trans WHERE {C.IN} AND closed=0")],
            {"discounted_open_invoice_count": cnt})

def h_disc_expiring(cx, C):
    d = int((re.search(r"next (\d+) days", C.q, re.I) or [0, 5])[1]) if re.search(r"next (\d+) days", C.q, re.I) else 5
    end = (E + dt.timedelta(days=d)).isoformat()
    cnt = (f"SELECT COUNT(*) FROM erp_cust_trans t JOIN erp_cash_disc d ON d.code=t.cash_disc_code "
           f"WHERE t.txn_type='Invoice' AND t.closed=0 "
           f"AND date(t.trans_date, '+' || d.days || ' days') BETWEEN '{EPOCH}' AND '{end}'")
    n = one(cx, cnt)
    f = {"expiring_invoice_count": (n, "number")}
    f["invoices"] = none_field(f"no open customer invoice carries a cash discount expiring by {end}") \
        if not n else (f"{n} invoices", "contains")
    return (f, [sqlstep(f"SELECT COUNT(*) AS open_invoices_with_discount_code FROM erp_cust_trans "
                        f"WHERE txn_type='Invoice' AND closed=0 AND cash_disc_code IS NOT NULL"),
                sqlstep("SELECT code, percent, days FROM erp_cash_disc")],
            {"expiring_invoice_count": cnt})

# --- collections ------------------------------------------------------------
def h_collections_pool(cx, C):
    sql = ("SELECT (SELECT COUNT(*) FROM erp_customers) - "
           "(SELECT COUNT(*) FROM erp_customer_pool)")
    return ({"unassigned_customer_count": (one(cx, sql), "number")},
            [sqlstep("SELECT COUNT(*) AS customers FROM erp_customers"),
             sqlstep("SELECT COUNT(*) AS assigned FROM erp_customer_pool")],
            {"unassigned_customer_count": sql})

def _letters(cx, C, answer_field, what):
    cnt = f"SELECT COUNT(*) FROM erp_collection_letters WHERE {C.IN}"
    n = one(cx, cnt)
    f = {"collection_letter_count": (n, "number")}
    f[answer_field] = none_field(f"no collection letter has ever been issued to this customer") \
        if not n else (str(cx.execute(f"SELECT letter_code FROM erp_collection_letters WHERE {C.IN} "
                                      f"ORDER BY letter_date DESC LIMIT 1").fetchone()[0]), "contains")
    return (f, [("data_find_entities", {"entity": "CollectionLetters", "filters": {"account": C.acct}}),
                sqlstep(f"SELECT letter_code, letter_date, status FROM erp_collection_letters WHERE {C.IN}")],
            {"collection_letter_count": cnt})

def h_letter_level(cx, C):  return _letters(cx, C, "current_letter_level", "level")
def h_last_letter(cx, C):   return _letters(cx, C, "last_letter_date", "date")
def h_letters_sent(cx, C):  return _letters(cx, C, "collection_letters", "letters")

def h_collections_tasks(cx, C):
    cnt = f"SELECT COUNT(*) FROM erp_activities WHERE {C.IN} AND closed=0"
    rows = cx.execute(f"SELECT purpose FROM erp_activities WHERE {C.IN} AND closed=0").fetchall()
    f = {"open_activity_count": (len(rows), "number")}
    f["open_activity_purpose"] = (rows[0][0], "contains") if rows else \
        none_field("this customer has no open collections activity")
    return (f, [("data_find_entities", {"entity": "Activities", "filters": {"account": C.acct}})],
            {"open_activity_count": cnt})

def h_worklist(cx, C):
    day = date_arg(C.q, EPOCH)
    cnt = (f"SELECT COUNT(DISTINCT account) FROM erp_activities "
           f"WHERE closed=0 AND start_date <= '{day}' AND COALESCE(end_date, start_date) >= '{day}'")
    n = one(cx, cnt)
    f = {"worklist_customer_count": (n, "number")}
    f["worklist_customers"] = none_field(f"no open collections activity is scheduled for {day}") \
        if not n else (", ".join(a for (a,) in cx.execute(
            f"SELECT DISTINCT account FROM erp_activities WHERE closed=0 AND start_date <= '{day}' "
            f"AND COALESCE(end_date, start_date) >= '{day}'")), "contains")
    return (f, [("data_find_entities", {"entity": "Activities", "filters": {"closed": 0}}),
                sqlstep("SELECT activity_id, account, start_date, end_date, closed FROM erp_activities")],
            {"worklist_customer_count": cnt})

# --- sales orders -----------------------------------------------------------
def h_so_hold(cx, C):
    rows = cx.execute("SELECT sales_id FROM erp_sales_orders WHERE hold_code='Do not process'").fetchall()
    return ({"order_count": (len(rows), "number"),
             "sales_order_id": (rows[0][0], "contains") if rows else
                               none_field("no sales order is marked 'Do not process'")},
            [("data_find_entities", {"entity": "SalesOrders", "filters": {"hold_code": "Do not process"}})],
            {"order_count": "SELECT COUNT(*) FROM erp_sales_orders WHERE hold_code='Do not process'"})

def h_so_by_status(cx, C):
    m = re.search(r"[\"']([A-Za-z ]+)[\"']\s*status", C.q, re.I)
    st = m.group(1).strip() if m else "Open"
    cnt = f"SELECT COUNT(*) FROM erp_sales_orders WHERE LOWER(status) LIKE '%{qq(st.lower())}%'"
    n = one(cx, cnt)
    pop = "SELECT COUNT(*) FROM erp_sales_orders"
    f = {"sales_order_count": (n, "number"), "sales_orders_in_usmf": (one(cx, pop), "number")}
    f["sales_order_ids"] = none_field(f"no sales order in USMF has status '{st}'") if not n else \
        (", ".join(s for (s,) in cx.execute(
            f"SELECT sales_id FROM erp_sales_orders WHERE LOWER(status) LIKE '%{qq(st.lower())}%'")), "contains")
    return (f, [sqlstep("SELECT sales_id, status, hold_code FROM erp_sales_orders")],
            {"sales_order_count": cnt, "sales_orders_in_usmf": pop})

def h_so_top_customer(cx, C):
    rows = cx.execute("""SELECT customer_name, COUNT(*) AS orders FROM erp_sales_orders
                         WHERE status LIKE 'Open%' GROUP BY account ORDER BY orders DESC""").fetchall()
    if not rows: return None
    top = rows[0][1]
    names = [r[0] for r in rows if r[1] == top]
    return ({"max_open_orders_per_customer": (top, "number"), "customer_names": (names, "all")},
            [sqlstep("SELECT account, customer_name, status FROM erp_sales_orders")],
            {"max_open_orders_per_customer":
                "SELECT MAX(orders) FROM (SELECT COUNT(*) AS orders FROM erp_sales_orders "
                "WHERE status LIKE 'Open%' GROUP BY account)"})

def h_so_largest(cx, C):
    rows = cx.execute(f"SELECT sales_id, ROUND(amount,2) FROM erp_sales_orders WHERE {C.IN} "
                      f"ORDER BY amount DESC").fetchall()
    f = {"order_count": (len(rows), "number")}
    if rows:
        f["largest_sales_order_id"] = (rows[0][0], "contains")
        f["largest_order_amount"] = (rows[0][1], "number")
    else:
        f["largest_sales_order_id"] = none_field("this customer has no sales orders in USMF")
    return (f, [("data_find_entities", {"entity": "SalesOrders", "filters": {"account": C.acct}})],
            {"order_count": f"SELECT COUNT(*) FROM erp_sales_orders WHERE {C.IN}",
             **({"largest_order_amount": f"SELECT ROUND(MAX(amount),2) FROM erp_sales_orders WHERE {C.IN}"}
                if rows else {})})

def h_so_open_for(cx, C):
    cnt = f"SELECT COUNT(*) FROM erp_sales_orders WHERE {C.IN} AND status LIKE 'Open%'"
    rows = cx.execute(f"SELECT sales_id FROM erp_sales_orders WHERE {C.IN} AND status LIKE 'Open%'").fetchall()
    return ({"open_sales_order_count": (len(rows), "number"),
             "sales_order_id": (rows[0][0], "contains") if rows else
                               none_field("this customer has no open sales orders")},
            [("data_find_entities", {"entity": "SalesOrders", "filters": {"account": C.acct}})],
            {"open_sales_order_count": cnt})

def h_sales_orders(cx, C):
    cnt = f"SELECT COUNT(*) FROM erp_sales_orders WHERE {C.IN}"
    rows = cx.execute(f"SELECT sales_id, status FROM erp_sales_orders WHERE {C.IN}").fetchall()
    return ({"order_count": (len(rows), "number"),
             "sales_order_id": (rows[0][0], "contains") if rows else
                               none_field("this customer has no sales orders in USMF")},
            [("data_find_entities", {"entity": "SalesOrders", "filters": {"account": C.acct}})],
            {"order_count": cnt})

# --- AP ---------------------------------------------------------------------
def h_vendor_balance(cx, C):
    w = f"{C.IN} AND txn_type='Invoice' AND closed=0"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"open_invoice_count": (n, "number")}
    f["ap_balance"] = (r2(one(cx, tot)), "number") if n else \
        none_field("nothing is owed to this vendor — no open AP invoices")
    return (f, [sqlstep(f"SELECT invoice, due_date, ROUND(amount-settled,2) AS open "
                        f"FROM erp_vend_trans WHERE {w}")],
            {"open_invoice_count": cnt, **({"ap_balance": tot} if n else {})})

def h_vendor_balance_ccy(cx, C):
    m = re.search(r"\b(EUR|USD|GBP|CHF)\b", C.q)
    if not m: return None
    ccy = m.group(1)
    w = f"currency='{ccy}' AND txn_type='Invoice' AND closed=0"
    tot = f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans WHERE {w}"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    return ({"ap_balance": (r2(one(cx, tot)), "number"), "currency": (ccy, "contains"),
             "open_invoice_count": (one(cx, cnt), "number")},
            [sqlstep(f"SELECT currency, COUNT(*) AS invoices, ROUND(SUM(amount-settled),2) AS ap_balance "
                     f"FROM erp_vend_trans WHERE txn_type='Invoice' AND closed=0 GROUP BY currency")],
            {"ap_balance": tot, "open_invoice_count": cnt})

def h_ap_by_currency(cx, C):
    rows = cx.execute("SELECT currency, ROUND(SUM(amount-settled),2) FROM erp_vend_trans "
                      "WHERE txn_type='Invoice' AND closed=0 GROUP BY currency ORDER BY 2 DESC").fetchall()
    f = {"currency_count": (len(rows), "number")}
    sqls = {"currency_count": "SELECT COUNT(DISTINCT currency) FROM erp_vend_trans "
                              "WHERE txn_type='Invoice' AND closed=0"}
    for ccy, amt in rows:
        k = f"{ccy.lower()}_ap_balance"
        f[k] = (r2(amt), "number")
        sqls[k] = (f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans "
                   f"WHERE txn_type='Invoice' AND closed=0 AND currency='{ccy}'")
    return (f, [sqlstep("SELECT currency, ROUND(SUM(amount-settled),2) AS ap_balance FROM erp_vend_trans "
                        "WHERE txn_type='Invoice' AND closed=0 GROUP BY currency")], sqls)

def h_ap_by_group(cx, C):
    sql = ("SELECT v.vendor_group, ROUND(SUM(t.amount-t.settled),2) AS ap_balance "
           "FROM erp_vend_trans t JOIN erp_vendors v ON v.account=t.account "
           "WHERE t.txn_type='Invoice' AND t.closed=0 GROUP BY v.vendor_group ORDER BY ap_balance DESC")
    rows = cx.execute(sql).fetchall()
    if not rows: return None
    return ({"vendor_group_count": (len(rows), "number"),
             "largest_vendor_group": (rows[0][0], "contains"),
             "largest_group_ap_balance": (r2(rows[0][1]), "number")},
            [sqlstep(sql)],
            {"largest_group_ap_balance":
                f"SELECT ROUND(COALESCE(SUM(t.amount-t.settled),0),2) FROM erp_vend_trans t "
                f"JOIN erp_vendors v ON v.account=t.account WHERE t.txn_type='Invoice' AND t.closed=0 "
                f"AND v.vendor_group='{qq(rows[0][0])}'"})

def h_ap_group_named(cx, C):
    m = re.search(r"vendor group [\"']([^\"']+)[\"']", C.q, re.I)
    if not m: return None
    g = m.group(1)
    cnt = f"SELECT COUNT(*) FROM erp_vendors WHERE LOWER(vendor_group)='{qq(g.lower())}'"
    tot = (f"SELECT ROUND(COALESCE(SUM(t.amount-t.settled),0),2) FROM erp_vend_trans t "
           f"JOIN erp_vendors v ON v.account=t.account WHERE t.txn_type='Invoice' AND t.closed=0 "
           f"AND LOWER(v.vendor_group)='{qq(g.lower())}'")
    n = one(cx, cnt)
    ngrp = "SELECT COUNT(DISTINCT vendor_group) FROM erp_vendors"
    f = {"vendors_in_group": (n, "number"), "vendor_group_count": (one(cx, ngrp), "number")}
    f["ap_balance"] = (r2(one(cx, tot)), "number") if n else \
        none_field(f"USMF has no vendor group '{g}' — the vendor groups on file are 10, 20, 30, 40 and 50")
    return (f, [sqlstep("SELECT vendor_group, COUNT(*) AS vendors FROM erp_vendors GROUP BY vendor_group")],
            {"vendors_in_group": cnt, "vendor_group_count": ngrp,
             **({"ap_balance": tot} if n else {})})

def h_ap_overdue(cx, C):
    w = f"txn_type='Invoice' AND closed=0 AND due_date < '{EPOCH}'"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans WHERE {w}"
    return ({"overdue_invoice_count": (one(cx, cnt), "number"),
             "overdue_ap_balance": (r2(one(cx, tot)), "number")},
            [sqlstep(f"SELECT COUNT(*) AS overdue_invoices, ROUND(SUM(amount-settled),2) AS overdue_ap "
                     f"FROM erp_vend_trans WHERE {w}")],
            {"overdue_invoice_count": cnt, "overdue_ap_balance": tot})

def h_ap_due_next_month(cx, C):
    start = (E.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
    end = (start + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)
    tag = start.strftime("%Y_%m")
    w = (f"txn_type='Invoice' AND closed=0 AND due_date BETWEEN '{start}' AND '{end}'")
    sql = (f"SELECT account, ROUND(SUM(amount-settled),2) AS due FROM erp_vend_trans WHERE {w} "
           f"GROUP BY account ORDER BY due DESC LIMIT 10")
    rows = cx.execute(sql).fetchall()
    if not rows: return None
    return ({f"total_due_{tag}": (r2(one(cx, f"SELECT ROUND(SUM(amount-settled),2) FROM erp_vend_trans WHERE {w}")), "number"),
             "top_vendor_account": (rows[0][0], "contains"),
             f"top_vendor_amount_due_{tag}": (r2(rows[0][1]), "number")},
            [sqlstep(sql)],
            {f"total_due_{tag}": f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans WHERE {w}",
             f"top_vendor_amount_due_{tag}":
                f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans WHERE {w} "
                f"AND account='{qq(rows[0][0])}'"})

def _ap_window(cx, prefix, start, end):
    w = f"txn_type='Invoice' AND closed=0 AND due_date BETWEEN '{start}' AND '{end}'"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans WHERE {w}"
    return ({f"{prefix}_count": (one(cx, cnt), "number"), f"{prefix}_total": (r2(one(cx, tot)), "number")},
            [sqlstep(f"SELECT invoice, account, due_date, ROUND(amount-settled,2) AS open "
                     f"FROM erp_vend_trans WHERE {w} LIMIT 25"),
             sqlstep(f"SELECT COUNT(*) AS invoices, ROUND(SUM(amount-settled),2) AS total "
                     f"FROM erp_vend_trans WHERE {w}")],
            {f"{prefix}_count": cnt, f"{prefix}_total": tot})

def h_ap_due_this_week(cx, C):
    end = (E + dt.timedelta(days=6 - E.weekday())).isoformat()
    return _ap_window(cx, "invoices_due_this_week", EPOCH, end)

def h_ap_due_7d(cx, C):
    d = days_arg(C.q, 7)
    end = (E + dt.timedelta(days=d - 1)).isoformat()
    return _ap_window(cx, f"ap_obligation_next_{d}_days", EPOCH, end)

def h_ap_posted_on(cx, C):
    day = date_arg(C.q, EPOCH)
    w = f"txn_type='Invoice' AND trans_date='{day}'"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount),0),2) FROM erp_vend_trans WHERE {w}"
    return ({"invoice_count": (one(cx, cnt), "number"), "invoiced_total": (r2(one(cx, tot)), "number")},
            [sqlstep(f"SELECT invoice, account, ROUND(amount,2) AS amount FROM erp_vend_trans WHERE {w}")],
            {"invoice_count": cnt, "invoiced_total": tot})

def h_ap_open_all(cx, C):
    w = "txn_type='Invoice' AND closed=0"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans WHERE {w}"
    return ({"pending_invoice_count": (one(cx, cnt), "number"),
             "pending_invoice_total": (r2(one(cx, tot)), "number")},
            [sqlstep(f"SELECT COUNT(*) AS pending, ROUND(SUM(amount-settled),2) AS total "
                     f"FROM erp_vend_trans WHERE {w}")],
            {"pending_invoice_count": cnt, "pending_invoice_total": tot})

def h_ap_invoices(cx, C):
    w = f"{C.IN} AND txn_type='Invoice' AND closed=0"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"open_invoice_count": (n, "number")}
    f["open_invoice_total"] = (r2(one(cx, tot)), "number") if n else \
        none_field("this vendor has no invoices awaiting payment")
    return (f, [sqlstep(f"SELECT invoice, due_date, ROUND(amount-settled,2) AS open "
                        f"FROM erp_vend_trans WHERE {w}")],
            {"open_invoice_count": cnt, **({"open_invoice_total": tot} if n else {})})

def h_three_way_match(cx, C):
    po = f"SELECT COUNT(*) FROM erp_purch_orders WHERE vendor IN {in_list(C.accts)}"
    n = one(cx, po)
    if n: return None       # this world only carries a PO for one vendor; never fake a match
    return ({"purchase_order_count": (0, "number"),
             "match_status": none_field("no purchase order or product receipt exists for this vendor, "
                                        "so no three-way match can be performed")},
            [("data_find_entities", {"entity": "PurchaseOrders", "filters": {"vendor": C.acct}}),
             sqlstep("SELECT po_number, vendor, status FROM erp_purch_orders")], {"purchase_order_count": po})

def h_purchase_orders(cx, C):
    cnt = f"SELECT COUNT(*) FROM erp_purch_orders WHERE vendor IN {in_list(C.accts)} AND status='Open'"
    rows = cx.execute(f"SELECT po_number FROM erp_purch_orders WHERE vendor IN {in_list(C.accts)} "
                      f"AND status='Open'").fetchall()
    return ({"open_po_count": (len(rows), "number"),
             "purchase_order_number": (rows[0][0], "contains") if rows else
                                      none_field("this vendor has no open purchase orders")},
            [("data_find_entities", {"entity": "PurchaseOrders", "filters": {"vendor": C.acct}})],
            {"open_po_count": cnt})

def h_vendors_discount(cx, C):
    code = cx.execute(f"SELECT cash_disc_code FROM erp_vendors WHERE account='{qq(C.acct)}'").fetchone()[0]
    if not code:
        return ({"offers_discount": ("no", "yes_no"),
                 "discount_code": none_field("no cash discount code is set on this vendor")},
                [("data_find_entities", {"entity": "Vendors", "filters": {"account": C.acct}})])
    pct = one(cx, f"SELECT percent FROM erp_cash_disc WHERE code='{qq(code)}'")
    return ({"offers_discount": ("yes", "yes_no"), "discount_code": (code, "contains"),
             "discount_percent": (pct, "number")},
            [("data_find_entities", {"entity": "Vendors", "filters": {"account": C.acct}}),
             ("data_find_entities", {"entity": "CashDiscounts", "filters": {"code": code}})],
            {"discount_percent": f"SELECT percent FROM erp_cash_disc WHERE code='{qq(code)}'"})

def h_vendor_terms(cx, C):
    r = cx.execute(f"SELECT payment_term FROM erp_vendors WHERE account='{qq(C.acct)}'").fetchone()
    if not r or not r[0]: return None
    days = one(cx, f"SELECT days FROM erp_payment_terms WHERE code='{qq(r[0])}'")
    return ({"payment_terms": (r[0], "contains"), "payment_term_days": (days, "number")},
            [("data_find_entities", {"entity": "Vendors", "filters": {"account": C.acct}}),
             ("data_find_entities", {"entity": "PaymentTerms", "filters": {"code": r[0]}})],
            {"payment_term_days": f"SELECT days FROM erp_payment_terms WHERE code='{qq(r[0])}'"})

def h_vendors_on_hold(cx, C):
    cnt = ("SELECT COUNT(*) FROM erp_vendors "
           "WHERE COALESCE(LOWER(on_hold),'no') NOT IN ('open','no','none')")
    n = one(cx, cnt)
    pop = "SELECT COUNT(*) FROM erp_vendors"
    f = {"vendors_on_payment_hold": (n, "number"), "vendors_reviewed": (one(cx, pop), "number")}
    f["vendor_accounts"] = none_field("no vendor in USMF is on payment hold") if not n else \
        (", ".join(a for (a,) in cx.execute(
            "SELECT account FROM erp_vendors WHERE COALESCE(LOWER(on_hold),'no') "
            "NOT IN ('open','no','none') LIMIT 10")), "contains")
    return (f, [sqlstep("SELECT on_hold, COUNT(*) AS vendors FROM erp_vendors GROUP BY on_hold")],
            {"vendors_on_payment_hold": cnt, "vendors_reviewed": pop})

def h_vendors_terms_over(cx, C):
    m = re.search(r"net\s*(\d+)", C.q, re.I)
    d = int(m.group(1)) if m else 60
    cnt = (f"SELECT COUNT(*) FROM erp_vendors v JOIN erp_payment_terms p ON p.code=v.payment_term "
           f"WHERE p.days > {d}")
    n = one(cx, cnt)
    longest = ("SELECT MAX(p.days) FROM erp_vendors v JOIN erp_payment_terms p ON p.code=v.payment_term")
    f = {"vendor_count": (n, "number"), "longest_payment_term_days": (one(cx, longest), "number")}
    f["vendor_accounts"] = none_field(f"no vendor in USMF has payment terms longer than Net {d} "
                                      f"— the longest term on the vendor master is Net45") if not n else \
        (", ".join(a for (a,) in cx.execute(
            f"SELECT v.account FROM erp_vendors v JOIN erp_payment_terms p ON p.code=v.payment_term "
            f"WHERE p.days > {d} LIMIT 10")), "contains")
    return (f, [sqlstep("SELECT payment_term, COUNT(*) AS vendors FROM erp_vendors GROUP BY payment_term"),
                sqlstep("SELECT code, days FROM erp_payment_terms ORDER BY days DESC")],
            {"vendor_count": cnt, "longest_payment_term_days": longest})

def h_ap_payments(cx, C):
    rows = {m: a for m, a in cx.execute("SELECT method, payment_account FROM erp_methods_of_payment "
                                        "WHERE side='vend'")}
    if "payroll" not in C.q.lower(): return None
    return ({"payroll_ck_account": (rows.get("Payroll_CK", "none"), "contains"),
             "check_account": (rows.get("CHECK", "none"), "contains")},
            [("data_find_entities", {"entity": "MethodsOfPayment", "filters": {"side": "vend"}})])

def h_payment_proposal(cx, C):
    j = re.search(r"journal\s+(\w+)", C.q, re.I)
    cnt = ("SELECT COUNT(*) FROM erp_payment_runs" if not j else
           f"SELECT COUNT(*) FROM erp_payment_runs WHERE run_id='{qq(j.group(1))}'")
    n = one(cx, cnt)
    if n: return None                       # no proposal exists in this world; never invent one
    wants_value = any(k in C.q.lower() for k in ("value", "total", "amount"))
    f = {"payment_run_count": (0, "number")}
    f["proposal_total" if wants_value else "vendors_included"] = none_field(
        "no payment proposal exists in USMF — the payment run table is empty")
    return (f, [("data_find_entities", {"entity": "PaymentRuns", "filters": {}}),
                sqlstep("SELECT run_id, pay_date, state FROM erp_payment_runs")],
            {"payment_run_count": cnt})

def h_vendor_payment_history(cx, C):
    since = (E - dt.timedelta(days=365)).isoformat()
    w = f"{C.IN} AND txn_type='Payment' AND trans_date >= '{since}'"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(-amount),0),2) FROM erp_vend_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"payment_count": (n, "number")}
    f["total_paid"] = (r2(one(cx, tot)), "number") if n else \
        none_field(f"no payment to this vendor is posted since {since}")
    return (f, [sqlstep(f"SELECT voucher, trans_date, txn_type, ROUND(amount,2) AS amount "
                        f"FROM erp_vend_trans WHERE {C.IN}")],
            {"payment_count": cnt, **({"total_paid": tot} if n else {})})

def _vend_notes(cx, C, kind, count_field, answer_field, what):
    w = f"{C.IN} AND txn_type='{kind}' AND trans_date >= '{EPOCH[:4]}-01-01'"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    n = one(cx, cnt)
    f = {count_field: (n, "number")}
    f[answer_field] = none_field(f"no {what} from this vendor is posted in {EPOCH[:4]}") if not n else \
        (str(n) + f" {what}", "contains")
    return (f, [sqlstep(f"SELECT txn_type, COUNT(*) AS n FROM erp_vend_trans WHERE {C.IN} GROUP BY txn_type")],
            {count_field: cnt})

def h_vendor_credit_notes(cx, C):
    return _vend_notes(cx, C, "CreditNote", "credit_note_count", "credit_notes", "credit note")

def h_vendor_debit_notes(cx, C):
    w = f"{C.IN} AND txn_type='DebitNote'"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    n = one(cx, cnt)
    return ({"debit_notes_exist": ("yes" if n else "no", "yes_no"),
             "debit_note_count": (n, "number")},
            [sqlstep(f"SELECT txn_type, COUNT(*) AS n FROM erp_vend_trans WHERE {C.IN} GROUP BY txn_type")],
            {"debit_note_count": cnt})

def h_vendor_spend(cx, C):
    w = f"{C.IN} AND txn_type='Invoice' AND trans_date >= '{EPOCH[:4]}-01-01'"
    cnt = f"SELECT COUNT(*) FROM erp_vend_trans WHERE {w}"
    tot = f"SELECT ROUND(COALESCE(SUM(amount),0),2) FROM erp_vend_trans WHERE {w}"
    n = one(cx, cnt)
    f = {"invoice_count": (n, "number")}
    f["total_spend_fy"] = (r2(one(cx, tot)), "number") if n else \
        none_field(f"nothing has been invoiced by this vendor since {EPOCH[:4]}-01-01")
    return (f, [sqlstep(f"SELECT invoice, trans_date, ROUND(amount,2) AS amount FROM erp_vend_trans "
                        f"WHERE {C.IN} AND txn_type='Invoice'")],
            {"invoice_count": cnt, **({"total_spend_fy": tot} if n else {})})

# ================================= routing ==================================
# (keywords, handler, entity side or None, absent-trap fields)
# Keywords are lowercase substrings, or compiled regexes. The FIRST route whose wording is
# present in the question wins; a question matching no route is rejected, never re-homed.
YEAR_BEFORE_LEDGER = re.compile(r"\b(19\d\d|20[01]\d|202[0-4])\b")

def R(kw, fn, ent=None, absent=None):
    return {"kw": kw, "fn": fn, "ent": ent, "absent": absent}

ROUTES = {
    "Credit Limit": [
        R(["credit hold"], h_credit_hold),
        R(["over their credit limit", "exceeding the credit limit"], h_over_credit_limit),
        R(["available credit"], h_credit_available, "cust", ("available_credit", "matching_customer_count")),
        R(["utilis", "utiliz", "percentage of"], h_credit_utilisation, "cust",
          ("credit_utilisation_pct", "matching_customer_count")),
        R(["credit limit"], h_credit_limit, "cust", ("credit_limit", "matching_customer_count")),
    ],
    "Credit Rating": [
        R(["credit rating"], h_credit_rating, "cust", ("credit_rating", "matching_customer_count")),
    ],
    "Customer Setup": [
        R(["phone"], h_phone, "cust", ("phone_number", "matching_customer_count")),
        R(["contact information", "contact details"], h_contact, "cust",
          ("contact_information", "matching_customer_count")),
        R(["customer group"], h_customers_in_group),
        R(["as the currency", "currency as of"], h_customers_by_currency),
        R(["payment term", "terms are assigned", "terms assigned"], h_customer_setup, "cust",
          ("payment_terms", "matching_customer_count")),
    ],
    "Outstanding Balance": [
        R(["unpaid", "outstanding"], h_outstanding, "cust", ("unpaid_total", "matching_customer_count")),
    ],
    "Aged Balance": [
        R(["coming due"], h_due_window, "cust", ("amount_coming_due", "matching_customer_count")),
        R(["180+", "180 days"], h_aged_180),
        R(["aging bucket"], h_aging_all_buckets),
        R(["top 10", "top ten"], h_aged_topn),
        R(["aged balance", "aging breakdown", "aging summary", "overdue receivables", "breakdown of"],
          h_aged_buckets, "cust", ("aged_balance", "matching_customer_count")),
        R(["details for"], h_customer_details, "cust", ("customer_details", "matching_customer_count")),
        R(["balance", "outstanding", "unpaid"], h_customer_balance, "cust",
          ("open_balance", "matching_customer_count")),
    ],
    "Payment History": [
        R([YEAR_BEFORE_LEDGER], h_payments_in_year, "cust", ("payments", "matching_customer_count")),
        R(["largest payment", "payment history", "payments made", "payment made",
           "payments  cave", "what payments has"], h_payment_history, "cust",
          ("payments", "matching_customer_count")),
    ],
    "Cash Collections": [
        R(["collected"], h_cash_collections, "cust", ("total_collected_fy", "matching_customer_count")),
    ],
    "Invoicing History": [
        R(["largest invoice"], h_largest_invoice),
        R(["highest total invoiced"], h_top_invoiced_customer),
        R(["positive"], h_positive_txns, "cust", ("positive_transaction_total", "matching_customer_count")),
        R(["unpaid", "outstanding"], h_customer_balance, "cust", ("open_balance", "matching_customer_count")),
        R(["invoices generated", "list of the invoices", "invoicing", "number of invoices"],
          h_invoicing_history, "cust", ("invoiced_total", "matching_customer_count")),
    ],
    "Cash Disocunts": [
        R(["discount window", "within the discount"], h_cash_discounts, "cust",
          ("discount_payment_count", "matching_customer_count")),
        R(["expiring"], h_disc_expiring),
        R(["discount terms", "cash discount terms"], h_cust_disc_terms, "cust",
          ("has_active_cash_discount", "matching_customer_count")),
    ],
    "Credit Notes": [
        R(["credit note"], h_credit_notes, "cust", ("unapplied_credit_total", "matching_customer_count")),
    ],
    "Dispute": [
        R(["dispute"], h_dispute, "cust", ("disputed_transactions", "matching_customer_count")),
    ],
    "Discounts": [
        R(["deduction"], h_deductions, "cust", ("open_deduction_total", "matching_customer_count")),
    ],
    "Collections": [
        R(["pool", "unassigned"], h_collections_pool),
        R(["letter level"], h_letter_level, "cust", ("current_letter_level", "matching_customer_count")),
        R(["last collection letter"], h_last_letter, "cust", ("last_letter_date", "matching_customer_count")),
        R(["collection letter"], h_letters_sent, "cust", ("collection_letters", "matching_customer_count")),
    ],
    "Collections Tasks": [
        R(["worklist"], h_worklist),
        R(["activit", "open task", "collections cases"], h_collections_tasks, "cust",
          ("open_activities", "matching_customer_count")),
    ],
    "Sales Orders": [
        R(["do not process"], h_so_hold),
        R(["most open sales orders"], h_so_top_customer),
        R(['"returned"', '"released"', "'returned'", "'released'"], h_so_by_status),
        R(["largest sales order"], h_so_largest, "cust", ("largest_sales_order_id", "matching_customer_count")),
        R(["open sales orders"], h_so_open_for, "cust", ("sales_order_id", "matching_customer_count")),
        R(["sales order"], h_sales_orders, "cust", ("sales_order_id", "matching_customer_count")),
    ],
    "AP Purchase Orders": [
        R(["purchase order"], h_purchase_orders, "vend", ("purchase_order_number", "matching_vendor_count")),
    ],
    "AP Invoices": [
        R(["this week"], h_ap_due_this_week),
        R(["posted"], h_ap_posted_on),
        R(["three-way match", "3-way match", "three way match"], h_three_way_match, "vend",
          ("match_status", "matching_vendor_count")),
        R(["how many vendor invoices"], h_ap_open_all),
        R(["pending approval", "open invoices", "invoices are pending"], h_ap_invoices, "vend",
          ("open_invoice_total", "matching_vendor_count")),
    ],
    "AP Payments": [
        R(["method of payment", "methods of payment", "payment account"], h_ap_payments),
        R(["payment proposal"], h_payment_proposal),
        R(["obligation"], h_ap_due_7d),
        R(["payment history"], h_vendor_payment_history, "vend", ("total_paid", "matching_vendor_count")),
    ],
    "Vendor Balance": [
        R(["overdue ap"], h_ap_overdue),
        R(['vendor group "', "vendor group '"], h_ap_group_named),
        R(["by vendor group"], h_ap_by_group),
        R(["due next month"], h_ap_due_next_month),
        R(["by currency"], h_ap_by_currency),
        R(["eur currency", "usd currency", "with eur", "with usd"], h_vendor_balance_ccy),
        R(["balance for", "owed to", "ap balance"], h_vendor_balance, "vend",
          ("ap_balance", "matching_vendor_count")),
    ],
    "Vendors": [
        R(["payment hold", "on hold"], h_vendors_on_hold),
        R(["longer than net"], h_vendors_terms_over),
        R(["discount"], h_vendors_discount, "vend", ("discount_code", "matching_vendor_count")),
        R(["payment terms for"], h_vendor_terms, "vend", ("payment_terms", "matching_vendor_count")),
        R(["balance owed", "outstanding balance"], h_vendor_balance, "vend",
          ("ap_balance", "matching_vendor_count")),
    ],
    "Other": [
        R(["credit note"], h_vendor_credit_notes, "vend", ("credit_notes", "matching_vendor_count")),
        R(["debit note"], h_vendor_debit_notes, "vend", ("debit_notes_exist", "matching_vendor_count")),
        R(["total spend", "spend with"], h_vendor_spend, "vend", ("total_spend_fy", "matching_vendor_count")),
    ],
}

# Questions that cannot be cloned honestly, with the reason printed in the skip report.
EXCLUDE = [
    (re.compile(r"\byyyy\b", re.I),
     "dataset typo — FB ships the literal placeholder 'yyyy' instead of a year"),
    (re.compile(r"new vendors created", re.I),
     "vendor master carries no creation date in this world; the truth is not re-derivable"),
    (re.compile(r"unposted vendor invoices", re.I),
     "no unposted-invoice register: erp_vend_trans is the posted subledger and has no posting-status field"),
]

def route(scenario, q):
    ql = q.lower()
    for r in ROUTES.get(scenario, []):
        for k in r["kw"]:
            if (k.search(q) if hasattr(k, "search") else k in ql):
                return r
    return None

# ================================= emission =================================
def emit(out_dir, name, query, scenario, segment, fields, steps, sqls=None, instance_of=None):
    """Write one Harbor task dir.

    `instance_of` distinguishes the two things this writer produces, which are NOT the same
    claim. Unset = a clone of a real benchmark question, carried verbatim. Set (to the pattern
    key) = an instance of that question's pattern with the entity substituted, generated by
    `world/etl/sweep_erp_qa.py`. Stamping both with the clone provenance is what let 1,026
    generated instances be counted as FinanceBenchmark parity and report 689% of addressable
    (docs/AUDIT.md A15).
    """
    sqls = sqls or {}
    d = out_dir / name
    (d / "tests").mkdir(parents=True, exist_ok=True)
    (d / "solution").mkdir(parents=True, exist_ok=True)
    walk = [{"server": "erp", "tool": t, "args": a} for t, a in steps]
    answers = {k: ("; ".join(str(x) for x in v) if kind == "all" else v)
               for k, (v, kind) in fields.items()}
    walk.append({"server": "harness", "tool": "submit_answer", "args": {"answers": answers}})
    (d / "solution/walk.json").write_text(json.dumps(walk, indent=1) + "\n")

    checks = {"answer_checks": [], "trace_checks": [
        {"type": "required_servers", "servers": ["erp"]}, {"type": "reads_before_submit"}],
        "state_checks": [{"type": "writes_only", "tables": ["answers"]}]}
    for k, (v, kind) in fields.items():
        if kind == "number":
            ac = {"field": k, "type": "number", "expect": v,
                  "tol_abs": 0.02 if isinstance(v, float) else 0}
            if k in sqls: ac["gt_sql"] = sqls[k]
            checks["answer_checks"].append(ac)
        elif kind == "contains":
            checks["answer_checks"].append({"field": k, "type": "contains_all", "expect": [str(v)]})
        elif kind == "all":
            checks["answer_checks"].append({"field": k, "type": "contains_all",
                                            "expect": [str(x) for x in v]})
        elif kind == "none":
            checks["answer_checks"].append({"field": k, "type": "none_answer"})
        elif kind == "yes_no":
            checks["answer_checks"].append({"field": k, "type": "yes_no", "expect": str(v)})
        else:
            checks["answer_checks"].append({"field": k, "type": "string", "expect": str(v)})
    (d / "tests/checks.json").write_text(json.dumps(checks, indent=1) + "\n")

    who = "Priya Shah · AP Manager" if segment == "AP" else "Casey Morgan · AR & Collections"
    # Question only. The reporting contract is served by the harness `reporting_fields` tool
    # from the seeded `answer_schema` — see sim/naturalize_prompts.py.
    (d / "instruction.md").write_text(f"**{who} · Teams**\n\n{query.strip()}\n")
    seedf = d / "environment/seed/mcp_seed.json"
    seedf.parent.mkdir(parents=True, exist_ok=True)
    payload = json.loads(seedf.read_text()) if seedf.exists() else {}
    payload["answer_schema"] = [
        {"ordinal": i, "field": k, "type": "number" if kind == "number" else "text",
         "description": ""}
        for i, (k, (_v, kind)) in enumerate(fields.items(), start=1)]
    seedf.write_text(json.dumps(payload, indent=1) + "\n")

    if instance_of:
        description = f"FinanceBenchmark erp_qa pattern instance — {segment} / {scenario}."
        keywords = '["finance", "erp_qa", "financebenchmark-pattern-instance"]'
        origin = (f"generated instance of the microsoft/FinanceBenchmark erp_qa pattern "
                  f"({segment} / {scenario}), entity substituted into the benchmark's phrasing "
                  f"by world/etl/sweep_erp_qa.py — NOT a verbatim benchmark question. Ground "
                  f"truth recomputed in-world (docs/AUDIT.md A3). Counted as patterns x "
                  f"instances, never as benchmark parity (docs/PARITY.md)")
        provenance = f'generated = true\npattern = "{instance_of}"\n'
    else:
        description = f"FinanceBenchmark erp_qa clone — {segment} / {scenario}."
        keywords = '["finance", "erp_qa", "financebenchmark-clone"]'
        origin = (f"clone of microsoft/FinanceBenchmark erp_qa ({segment} / {scenario}); "
                  f"question verbatim, ground truth recomputed in-world (docs/AUDIT.md A3)")
        provenance = "generated = false\n"

    (d / "task.toml").write_text(f'''schema_version = "1.4"

[task]
name = "{out_dir.name}/{name}"
version = "0.1.0"
description = "{description}"
authors = ["nario-ai"]
keywords = {keywords}

[metadata]
family = "{out_dir.name}"
origin = "{origin}"
{provenance}difficulty = "medium"
acceptance_label = "pending_calibration"
walk_len = {len(walk)}

[verifier]
timeout_sec = 120
[agent]
timeout_sec = 600
[environment]
cpus = 1
memory_mb = 1024
''')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-scenario", type=int, default=4)
    ap.add_argument("--out", default="tasks/erp_qa_fb")
    a = ap.parse_args()
    import yaml
    data = yaml.safe_load(DATASET.read_text())
    erp = [t for t in data if t.get("plugin") == "erp_qa"]
    cx = sqlite3.connect(DB)
    out_dir = ROOT / a.out
    made, per, skipped = 0, {}, []
    for t in erp:
        sc, seg, q = t.get("scenario"), t.get("segment"), t["query"]
        reason = next((why for rx, why in EXCLUDE if rx.search(q)), None)
        if reason:
            skipped.append((sc, q, reason)); continue
        r = route(sc, q)
        if not r:
            skipped.append((sc, q, "no route: the question's wording does not match any handler "
                                   "for this scenario (gate held; a mis-route would drift)"))
            continue
        if per.get(sc, 0) >= a.per_scenario: continue
        accts, name, side, missing = resolve(cx, q, seg)
        C = Ctx(cx, q, seg, accts, name, side, missing)
        res = None
        try:
            if r["ent"]:
                C.side = r["ent"]
                C.table = "erp_vendors" if C.side == "vend" else "erp_customers"
                if not accts:
                    if missing and r["absent"]:
                        res = h_absent(cx, C, *r["absent"])
                    if res is None:
                        why = "the entity the question names cannot be resolved to master data"
                        if missing:
                            why = (f"'{missing}' is absent from master data and this route has no "
                                   f"empty-answer form")
                        skipped.append((sc, q, why))
                        continue
                else:
                    res = r["fn"](cx, C)
            else:
                res = r["fn"](cx, C)
        except Exception as e:
            skipped.append((sc, q, f"handler error: {type(e).__name__}: {e}")); continue
        if not res:
            skipped.append((sc, q, "handler declined: the world has no re-derivable answer of the "
                                   "shape this question asks for")); continue
        fields, steps, sqls = (res + (None,))[:3] if len(res) < 3 else res
        per[sc] = per.get(sc, 0) + 1
        emit(out_dir, f"{slug(sc)}-{per[sc]}", q, sc, seg, fields, steps, sqls)
        made += 1
    print(f"generated {made} tasks into {a.out} (of {len(erp)} source questions)")
    for k, v in sorted(per.items()): print(f"   {k}: {v}")
    if skipped:
        print(f"\nexcluded ({len(skipped)}):")
        for sc, q, why in skipped:
            print(f" - [{sc}] {q.strip()[:110]}\n     reason: {why}")

if __name__ == "__main__":
    main()
