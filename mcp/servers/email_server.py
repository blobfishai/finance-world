#!/usr/bin/env python3
"""Email MCP server — read-only view of the AP/AR shared mailbox. SIMULATION ONLY."""
import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("email", "Shared finance mailbox (ap@ / ar@ contoso-sim). Read-only. SIMULATION ONLY.")

@S.tool("search_messages", "Search messages by keyword over subject/body/sender.",
        {"query": {"type": "string"}, "folder": {"type": "string", "description": "default inbox"}}, ["query"])
def search_messages(query, folder="inbox"):
    cx = S.db()
    like = f"%{query.lower()}%"
    rows = cx.execute("""SELECT id, folder, from_addr, subject, sent_at, attachment_name
                         FROM email_messages
                         WHERE folder=? AND (LOWER(subject) LIKE ? OR LOWER(body) LIKE ? OR LOWER(from_addr) LIKE ?)
                         ORDER BY sent_at DESC LIMIT 25""", (folder, like, like, like)).fetchall()
    return {"matches": [dict(r) for r in rows]}

@S.tool("get_message", "Fetch a full message including attachment text.",
        {"message_id": {"type": "string"}}, ["message_id"])
def get_message(message_id):
    cx = S.db()
    r = cx.execute("SELECT * FROM email_messages WHERE id=?", (message_id,)).fetchone()
    return dict(r) if r else {"error": "not found"}

@S.tool("list_folders", "List mail folders (labels) with message counts.")
def list_folders():
    cx = S.db()
    return {"folders": [dict(r) for r in cx.execute(
        "SELECT folder, COUNT(*) AS messages FROM email_messages GROUP BY folder ORDER BY folder")]}

def _thread_key(subject):
    return re.sub(r"^\s*((re|fwd?|fw)\s*:\s*)+", "", (subject or "").lower()).strip()

@S.tool("get_thread", "Fetch the whole conversation thread a message belongs to (grouped by normalized subject).",
        {"message_id": {"type": "string"}}, ["message_id"])
def get_thread(message_id):
    cx = S.db()
    r = cx.execute("SELECT * FROM email_messages WHERE id=?", (message_id,)).fetchone()
    if not r: return {"error": "not found"}
    key = _thread_key(r["subject"])
    msgs = [dict(m) for m in cx.execute("SELECT * FROM email_messages ORDER BY sent_at")
            if _thread_key(m["subject"]) == key]
    return {"thread_subject": key, "message_count": len(msgs), "messages": msgs}

@S.tool("get_attachment", "Fetch a message's attachment content (text extraction).",
        {"message_id": {"type": "string"}}, ["message_id"])
def get_attachment(message_id):
    cx = S.db()
    r = cx.execute("SELECT attachment_name, attachment_text FROM email_messages WHERE id=?", (message_id,)).fetchone()
    if not r: return {"error": "not found"}
    if not r["attachment_name"]: return {"error": "message has no attachment"}
    return {"attachment_name": r["attachment_name"], "content": r["attachment_text"]}

if __name__ == "__main__":
    S.run()
