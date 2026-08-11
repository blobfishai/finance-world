#!/usr/bin/env python3
"""Email MCP server — 1:1 Gmail API shapes over the shared AP/AR mailbox. Read-only.

Mirrors Gmail v1: users.messages.list (q= search, returns {messages:[{id,threadId}],
resultSizeEstimate}), users.messages.get (payload.headers + snippet + body),
users.threads.get, users.labels.list, attachments.get. SIMULATION ONLY."""
import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("email", "Shared finance mailbox (ap@/ar@ contoso-sim), Gmail API shapes. Read-only. SIMULATION ONLY.")

def _thread_key(subject):
    return re.sub(r"^\s*((re|fwd?|fw)\s*:\s*)+", "", (subject or "").lower()).strip()

def _thread_id(subject):
    import hashlib
    return "t_" + hashlib.sha1(_thread_key(subject).encode()).hexdigest()[:10]

def _headers(r):
    return [{"name": "From", "value": r["from_addr"]}, {"name": "To", "value": r["to_addr"]},
            {"name": "Subject", "value": r["subject"]}, {"name": "Date", "value": r["sent_at"]}]

def _full(r):
    msg = {"id": r["id"], "threadId": _thread_id(r["subject"]),
           "labelIds": [r["folder"].upper()], "snippet": (r["body"] or "")[:120],
           "internalDate": r["sent_at"],
           "payload": {"mimeType": "multipart/mixed" if r["attachment_name"] else "text/plain",
                       "headers": _headers(r),
                       "body": {"data": r["body"]}}}
    if r["attachment_name"]:
        msg["payload"]["parts"] = [{"filename": r["attachment_name"],
                                    "body": {"attachmentId": f"att_{r['id']}", "size": len(r["attachment_text"] or "")}}]
    return msg

@S.tool("messages_list", "Search messages (users.messages.list). `q` matches subject/body/sender; optional label (default INBOX).",
        {"q": {"type": "string"}, "label": {"type": "string"}}, ["q"])
def messages_list(q, label="INBOX"):
    """Token search over subject/body/sender: every term must appear, in any order."""
    cx = S.db()
    terms = [t for t in re.findall(r"[a-z0-9@.\-]+", q.lower()) if len(t) > 2]
    rows = []
    for r in cx.execute("""SELECT id, subject, folder, from_addr, body, sent_at FROM email_messages
                           WHERE UPPER(folder)=? ORDER BY sent_at DESC""", (label.upper(),)):
        hay = f"{r['subject']} {r['body']} {r['from_addr']}".lower()
        if not terms or all(t in hay for t in terms): rows.append(r)
    rows = rows[:25]
    return {"messages": [{"id": r["id"], "threadId": _thread_id(r["subject"])} for r in rows],
            "resultSizeEstimate": len(rows)}

@S.tool("messages_get", "Fetch a full message (users.messages.get, format=full): headers, snippet, body, attachment parts.",
        {"id": {"type": "string"}}, ["id"])
def messages_get(id):
    cx = S.db()
    r = cx.execute("SELECT * FROM email_messages WHERE id=?", (id,)).fetchone()
    return _full(r) if r else {"error": {"code": 404, "message": f"Requested entity was not found: {id}"}}

@S.tool("threads_get", "Fetch a conversation thread (users.threads.get): all messages sharing the normalized subject.",
        {"id": {"type": "string", "description": "a threadId from messages_list, or a message id"}}, ["id"])
def threads_get(id):
    cx = S.db()
    all_rows = cx.execute("SELECT * FROM email_messages ORDER BY sent_at").fetchall()
    tid = id
    if not id.startswith("t_"):
        r = next((m for m in all_rows if m["id"] == id), None)
        if not r: return {"error": {"code": 404, "message": f"Requested entity was not found: {id}"}}
        tid = _thread_id(r["subject"])
    msgs = [_full(m) for m in all_rows if _thread_id(m["subject"]) == tid]
    if not msgs: return {"error": {"code": 404, "message": f"Requested entity was not found: {id}"}}
    return {"id": tid, "messages": msgs}

@S.tool("labels_list", "List labels/folders with message counts (users.labels.list).")
def labels_list():
    cx = S.db()
    return {"labels": [{"id": r["folder"].upper(), "name": r["folder"].upper(),
                        "messagesTotal": r["n"], "type": "system"}
                       for r in cx.execute("SELECT folder, COUNT(*) AS n FROM email_messages GROUP BY folder")]}

@S.tool("attachments_get", "Fetch an attachment's content by message id (users.messages.attachments.get; text extraction).",
        {"message_id": {"type": "string"}}, ["message_id"])
def attachments_get(message_id):
    cx = S.db()
    r = cx.execute("SELECT attachment_name, attachment_text FROM email_messages WHERE id=?", (message_id,)).fetchone()
    if not r: return {"error": {"code": 404, "message": f"Requested entity was not found: {message_id}"}}
    if not r["attachment_name"]: return {"error": {"code": 404, "message": "message has no attachment"}}
    return {"attachmentId": f"att_{message_id}", "filename": r["attachment_name"],
            "size": len(r["attachment_text"] or ""), "data": r["attachment_text"]}

@S.tool("send_message", "Send a message from the shared finance mailbox (users.messages.send shape). "
        "Counterparties reply on their own schedule; a reply, if any, lands in the inbox and is returned here.",
        {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
        ["to", "subject", "body"])
def send_message(to, subject, body):
    cx = S.db()
    n = cx.execute("SELECT COUNT(*) FROM email_messages WHERE folder='sent'").fetchone()[0] + 1
    sid = f"em-sent-{n:03d}"
    cx.execute("""INSERT INTO email_messages(id, folder, from_addr, to_addr, subject, sent_at, body,
                  attachment_name, attachment_text) VALUES(?,'sent','ap@contoso-sim.example',?,?,?,?,NULL,NULL)""",
               (sid, to, subject, S.now, body))
    hay = f"{to} {subject} {body}".lower()
    replies = []
    for r in cx.execute("SELECT * FROM email_npc_scripts"):
        if r["match_to"] and r["match_to"].lower() not in to.lower(): continue
        kws = [k.strip().lower() for k in (r["match_keywords"] or "").split(",") if k.strip()]
        if kws and not any(k in hay for k in kws): continue
        rid = f"em-reply-{r['id']}"
        if cx.execute("SELECT 1 FROM email_messages WHERE id=?", (rid,)).fetchone(): continue
        cx.execute("""INSERT INTO email_messages(id, folder, from_addr, to_addr, subject, sent_at, body,
                      attachment_name, attachment_text) VALUES(?,'inbox',?,'ap@contoso-sim.example',?,?,?,?,?)""",
                   (rid, r["reply_from"], r["reply_subject"], S.now, r["reply_body"],
                    r["attachment_name"], r["attachment_text"]))
        replies.append({"id": rid, "from": r["reply_from"], "subject": r["reply_subject"], "body": r["reply_body"]})
    cx.commit()
    return {"id": sid, "labelIds": ["SENT"], "threadId": _thread_id(subject),
            "replies_received": replies,
            "note": "no reply yet — the counterparty may not respond to this request" if not replies else None}

if __name__ == "__main__":
    S.run()
