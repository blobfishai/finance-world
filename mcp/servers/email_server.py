#!/usr/bin/env python3
"""Email MCP server — read-only view of the AP/AR shared mailbox. SIMULATION ONLY."""
import sys
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

if __name__ == "__main__":
    S.run()
