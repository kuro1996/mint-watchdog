"""SQLite storage for Mint Watchdog (single file, no server, no cost).

Database: ``server/store/mintwatch.db`` (gitignored — runtime data, not
source). Tables: leads, verifications, scores, alerts, holdings.

Status vocabulary (leads): NEW | VERIFYING | VERIFIED_FREE | PAID |
EXHAUSTED | AVOID | UNVERIFIED | STALE. STALE means "last read failed on
every endpoint" — it never means the candidate is closed.
"""

import json
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY,
    contract TEXT UNIQUE NOT NULL,
    name TEXT,
    source TEXT,
    source_url TEXT,
    first_seen TEXT,
    status TEXT DEFAULT 'NEW'
);
CREATE TABLE IF NOT EXISTS verifications (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER NOT NULL,
    checked_at TEXT NOT NULL,
    sourcify TEXT,
    total_supply INTEGER,
    free_left INTEGER,
    quota_left INTEGER,
    mint_price TEXT,
    paused INTEGER,
    owner TEXT,
    status TEXT,
    FOREIGN KEY (lead_id) REFERENCES leads (id)
);
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER NOT NULL,
    scored_at TEXT NOT NULL,
    total INTEGER,
    security INTEGER,
    investor_protection INTEGER,
    anti_manipulation INTEGER,
    transparency INTEGER,
    market_viability INTEGER,
    verdict TEXT,
    hard_cap INTEGER,
    reasons TEXT,
    missing TEXT,
    FOREIGN KEY (lead_id) REFERENCES leads (id)
);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    kind TEXT,
    message TEXT,
    seen INTEGER DEFAULT 0,
    FOREIGN KEY (lead_id) REFERENCES leads (id)
);
CREATE TABLE IF NOT EXISTS holdings (
    id INTEGER PRIMARY KEY,
    contract TEXT NOT NULL,
    token_id TEXT,
    name TEXT,
    locked INTEGER,
    floor_note TEXT
);
"""


def init_db(path):
    """Open (creating if needed) the database and ensure the schema."""
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def upsert_lead(conn, contract, name=None, source=None, source_url=None,
                first_seen=None, status="NEW"):
    """Insert a lead, or refresh its metadata if the contract is known."""
    cur = conn.execute(
        "INSERT INTO leads (contract, name, source, source_url, first_seen, status)"
        " VALUES (?, ?, ?, ?, ?, ?)"
        " ON CONFLICT(contract) DO UPDATE SET"
        " name=COALESCE(excluded.name, leads.name),"
        " source=COALESCE(excluded.source, leads.source),"
        " source_url=COALESCE(excluded.source_url, leads.source_url),"
        " status=excluded.status",
        (contract.lower(), name, source, source_url, first_seen, status),
    )
    conn.commit()
    return cur.lastrowid


def get_lead_id(conn, contract):
    row = conn.execute(
        "SELECT id FROM leads WHERE contract = ?", (contract.lower(),)
    ).fetchone()
    return row[0] if row else None


def add_verification(conn, lead_id, verification):
    conn.execute(
        "INSERT INTO verifications (lead_id, checked_at, sourcify,"
        " total_supply, free_left, quota_left, mint_price, paused, owner, status)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            lead_id,
            verification.get("checked_at"),
            verification.get("sourcify"),
            verification.get("total_supply"),
            verification.get("free_left"),
            verification.get("quota_left"),
            None if verification.get("mint_price") is None
            else str(verification["mint_price"]),
            None if verification.get("paused") is None
            else int(verification["paused"]),
            verification.get("owner"),
            verification.get("status"),
        ),
    )
    conn.commit()


def add_score(conn, lead_id, scored_at, score):
    cats = score["categories"]
    conn.execute(
        "INSERT INTO scores (lead_id, scored_at, total, security,"
        " investor_protection, anti_manipulation, transparency,"
        " market_viability, verdict, hard_cap, reasons, missing)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            lead_id,
            scored_at,
            score["total"],
            cats["security"],
            cats["investor_protection"],
            cats["anti_manipulation"],
            cats["transparency"],
            cats["market_viability"],
            score["verdict"],
            int(score["hard_cap_applied"]),
            json.dumps(score["reasons"]),
            json.dumps(score["missing"]),
        ),
    )
    conn.commit()


def add_alert(conn, lead_id, created_at, kind, message):
    conn.execute(
        "INSERT INTO alerts (lead_id, created_at, kind, message) VALUES (?, ?, ?, ?)",
        (lead_id, created_at, kind, message),
    )
    conn.commit()


def add_holding(conn, contract, token_id=None, name=None, locked=None,
                floor_note="no verified floor"):
    conn.execute(
        "INSERT INTO holdings (contract, token_id, name, locked, floor_note)"
        " VALUES (?, ?, ?, ?, ?)",
        (
            contract.lower(),
            None if token_id is None else str(token_id),
            name,
            None if locked is None else int(locked),
            floor_note,
        ),
    )
    conn.commit()


def list_holdings(conn):
    """All recorded holdings (for the dashboard holdings view)."""
    rows = conn.execute(
        "SELECT contract, token_id, name, locked, floor_note"
        " FROM holdings ORDER BY id DESC"
    ).fetchall()
    return [
        {
            "contract": r[0], "token_id": r[1], "name": r[2],
            "locked": None if r[3] is None else bool(r[3]),
            "floor_note": r[4],
        }
        for r in rows
    ]


def get_lead_detail(conn, contract):
    """One lead with its latest verification and latest score, or None.

    Returned score includes per-category numbers plus the reasons and
    missing-field lists (parsed from JSON), so the dashboard candidate
    page can show the full rubric breakdown without a second call.
    """
    row = conn.execute(
        "SELECT id, contract, name, source, source_url, first_seen, status"
        " FROM leads WHERE contract = ?",
        (contract.lower(),),
    ).fetchone()
    if row is None:
        return None
    lead_id = row[0]
    ver = conn.execute(
        "SELECT checked_at, sourcify, total_supply, free_left, quota_left,"
        " mint_price, paused, owner, status FROM verifications"
        " WHERE lead_id = ? ORDER BY id DESC LIMIT 1",
        (lead_id,),
    ).fetchone()
    sc = conn.execute(
        "SELECT scored_at, total, security, investor_protection,"
        " anti_manipulation, transparency, market_viability, verdict,"
        " hard_cap, reasons, missing FROM scores"
        " WHERE lead_id = ? ORDER BY id DESC LIMIT 1",
        (lead_id,),
    ).fetchone()
    detail = {
        "id": row[0], "contract": row[1], "name": row[2], "source": row[3],
        "source_url": row[4], "first_seen": row[5], "status": row[6],
        "verification": None, "score": None,
    }
    if ver is not None:
        detail["verification"] = {
            "checked_at": ver[0], "sourcify": ver[1],
            "total_supply": ver[2], "free_left": ver[3],
            "quota_left": ver[4], "mint_price": ver[5],
            "paused": None if ver[6] is None else bool(ver[6]),
            "owner": ver[7], "status": ver[8],
        }
    if sc is not None:
        detail["score"] = {
            "scored_at": sc[0], "total": sc[1],
            "categories": {
                "security": sc[2], "investor_protection": sc[3],
                "anti_manipulation": sc[4], "transparency": sc[5],
                "market_viability": sc[6],
            },
            "verdict": sc[7], "hard_cap_applied": bool(sc[8]),
            "reasons": json.loads(sc[9] or "[]"),
            "missing": json.loads(sc[10] or "[]"),
        }
    return detail


def list_leads(conn):
    """Leads with their latest verification + score (for the API/dashboard)."""
    rows = conn.execute(
        "SELECT l.id, l.contract, l.name, l.source, l.source_url,"
        " l.first_seen, l.status,"
        " (SELECT total FROM scores WHERE lead_id = l.id ORDER BY id DESC LIMIT 1),"
        " (SELECT verdict FROM scores WHERE lead_id = l.id ORDER BY id DESC LIMIT 1),"
        " (SELECT free_left FROM verifications WHERE lead_id = l.id"
        "  ORDER BY id DESC LIMIT 1),"
        " (SELECT quota_left FROM verifications WHERE lead_id = l.id"
        "  ORDER BY id DESC LIMIT 1)"
        " FROM leads l ORDER BY l.id DESC"
    ).fetchall()
    return [
        {
            "id": r[0], "contract": r[1], "name": r[2], "source": r[3],
            "source_url": r[4], "first_seen": r[5], "status": r[6],
            "score_total": r[7], "score_verdict": r[8],
            "free_left": r[9], "quota_left": r[10],
        }
        for r in rows
    ]
