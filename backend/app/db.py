import os, sqlite3
from pathlib import Path

DB = os.getenv("SLOTLOOP_DB", str(Path(__file__).resolve().parents[1] / "slotloop.db"))

def connect():
    Path(DB).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB, timeout=15, isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("PRAGMA journal_mode=WAL")
    return c

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS businesses(
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, service TEXT NOT NULL,
          area TEXT NOT NULL, address TEXT NOT NULL, description TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS slots(
          id INTEGER PRIMARY KEY, business_id INTEGER NOT NULL REFERENCES businesses(id),
          starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, price INTEGER NOT NULL CHECK(price>=0),
          original_price INTEGER, status TEXT NOT NULL DEFAULT 'available'
          CHECK(status IN ('available','booked','cancelled')), created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS bookings(
          id INTEGER PRIMARY KEY, slot_id INTEGER NOT NULL UNIQUE REFERENCES slots(id),
          customer_name TEXT NOT NULL, customer_email TEXT NOT NULL, amount INTEGER NOT NULL,
          status TEXT NOT NULL DEFAULT 'confirmed', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS idx_slots_search ON slots(status, starts_at, price);
        """)
        if c.execute("SELECT COUNT(*) FROM businesses").fetchone()[0] == 0:
            c.executemany("INSERT INTO businesses(name,service,area,address,description) VALUES(?,?,?,?,?)", [
              ("Studio A Andheri","Haircut","Andheri West","Lokhandwala, Andheri West","Fictional demo listing"),
              ("The Groom Room","Haircut","Andheri West","Four Bungalows, Andheri West","Fictional demo listing"),
              ("Glow Nail Studio","Nail appointment","Andheri West","Oshiwara, Andheri West","Fictional demo listing"),
              ("CourtSide Arena","Badminton court","Andheri West","Veera Desai Road, Andheri West","Fictional demo listing"),
              ("Studio B Andheri","Hair colouring","Andheri East","Chakala, Andheri East","Fictional demo listing")])
            c.executemany("INSERT INTO slots(business_id,starts_at,ends_at,price,original_price) VALUES(?,?,?,?,?)", [
              (1,"2026-11-01T16:30:00","2026-11-01T17:15:00",350,550),
              (2,"2026-11-01T17:15:00","2026-11-01T18:00:00",400,600),
              (1,"2026-11-01T18:00:00","2026-11-01T18:45:00",300,500),
              (3,"2026-11-01T19:00:00","2026-11-01T20:00:00",450,650),
              (4,"2026-11-01T20:00:00","2026-11-01T21:00:00",500,700),
              (5,"2026-11-02T12:00:00","2026-11-02T13:30:00",900,1400),
              (2,"2026-11-02T16:00:00","2026-11-02T16:45:00",375,550)])
