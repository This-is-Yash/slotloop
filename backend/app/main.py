from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from .db import connect, init_db

app = FastAPI(title="SLOTLOOP API", version="1.0.0",
 description="Prototype marketplace for expiring business capacity. Seed data is fictional.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup(): init_db()

class BookingIn(BaseModel):
    slot_id: int
    customer_name: str = Field(min_length=2, max_length=80)
    customer_email: str = Field(min_length=5, max_length=160)

class SlotIn(BaseModel):
    starts_at: str
    ends_at: str
    price: int = Field(ge=0, le=100000)
    original_price: int | None = Field(default=None, ge=0, le=100000)

def slot_out(r):
    d = dict(r)
    d["discount_percent"] = round((1-d["price"]/d["original_price"])*100) if d.get("original_price") else 0
    return d

@app.get("/api/health")
def health(): return {"status":"ok","data_notice":"Seed data is fictional demo data."}

@app.get("/api/services")
def services():
    with connect() as c: return [r[0] for r in c.execute("SELECT DISTINCT service FROM businesses ORDER BY service")]

@app.get("/api/businesses")
def businesses():
    with connect() as c: return [dict(r) for r in c.execute("SELECT * FROM businesses ORDER BY name")]

@app.get("/api/slots")
def slots(service: str="", area: str="", max_price: int=Query(100000,ge=0)):
    sql = """SELECT s.*,b.name business_name,b.service,b.area,b.address
             FROM slots s JOIN businesses b ON b.id=s.business_id
             WHERE s.status='available' AND s.price<=?"""
    args=[max_price]
    if service: sql += " AND lower(b.service)=lower(?)"; args.append(service)
    if area: sql += " AND lower(b.area) LIKE lower(?)"; args.append("%"+area+"%")
    sql += " ORDER BY s.starts_at,s.price"
    with connect() as c: return [slot_out(r) for r in c.execute(sql,args)]

@app.post("/api/bookings", status_code=201)
def book(p: BookingIn):
    with connect() as c:
        try:
            c.execute("BEGIN IMMEDIATE")
            s=c.execute("SELECT * FROM slots WHERE id=?",(p.slot_id,)).fetchone()
            if not s:
                c.execute("ROLLBACK"); raise HTTPException(404,"Slot not found")
            if s["status"]!="available":
                c.execute("ROLLBACK"); raise HTTPException(409,"Slot is no longer available. Refresh.")
            changed=c.execute("UPDATE slots SET status='booked' WHERE id=? AND status='available'",(p.slot_id,))
            if changed.rowcount != 1:
                c.execute("ROLLBACK"); raise HTTPException(409,"Someone else just booked this slot.")
            cur=c.execute("INSERT INTO bookings(slot_id,customer_name,customer_email,amount) VALUES(?,?,?,?)",
                (p.slot_id,p.customer_name.strip(),p.customer_email.strip().lower(),s["price"]))
            row=dict(c.execute("SELECT * FROM bookings WHERE id=?",(cur.lastrowid,)).fetchone())
            c.execute("COMMIT")
            return row
        except HTTPException: raise
        except Exception:
            c.execute("ROLLBACK"); raise

@app.get("/api/businesses/{business_id}/dashboard")
def dashboard(business_id:int):
    with connect() as c:
        b=c.execute("SELECT * FROM businesses WHERE id=?",(business_id,)).fetchone()
        if not b: raise HTTPException(404,"Business not found")
        m=c.execute("""SELECT COUNT(*) total_slots,
          SUM(status='available') available_slots,SUM(status='booked') recovered_bookings,
          COALESCE(SUM(CASE WHEN status='booked' THEN price ELSE 0 END),0) recovered_revenue
          FROM slots WHERE business_id=?""",(business_id,)).fetchone()
        rows=c.execute("""SELECT s.*,b.name business_name,b.service,b.area,b.address FROM slots s
          JOIN businesses b ON b.id=s.business_id WHERE s.business_id=? ORDER BY s.starts_at DESC""",(business_id,)).fetchall()
        return {"business":dict(b),"metrics":dict(m),"slots":[slot_out(r) for r in rows]}

@app.post("/api/businesses/{business_id}/slots",status_code=201)
def add_slot(business_id:int,p:SlotIn):
    try:
        if datetime.fromisoformat(p.ends_at)<=datetime.fromisoformat(p.starts_at): raise ValueError()
    except ValueError: raise HTTPException(422,"Provide valid ISO timestamps; end must be after start.")
    with connect() as c:
        if not c.execute("SELECT 1 FROM businesses WHERE id=?",(business_id,)).fetchone():
            raise HTTPException(404,"Business not found")
        cur=c.execute("INSERT INTO slots(business_id,starts_at,ends_at,price,original_price) VALUES(?,?,?,?,?)",
          (business_id,p.starts_at,p.ends_at,p.price,p.original_price))
        r=c.execute("""SELECT s.*,b.name business_name,b.service,b.area,b.address FROM slots s
          JOIN businesses b ON b.id=s.business_id WHERE s.id=?""",(cur.lastrowid,)).fetchone()
        return slot_out(r)

@app.patch("/api/slots/{slot_id}/cancel")
def cancel(slot_id:int):
    with connect() as c:
        r=c.execute("UPDATE slots SET status='cancelled' WHERE id=? AND status='available'",(slot_id,))
        if r.rowcount!=1: raise HTTPException(409,"Only available slots can be cancelled.")
        return {"status":"cancelled","slot_id":slot_id}

@app.get("/api/metrics/summary")
def summary():
    with connect() as c:
        r=dict(c.execute("""SELECT COUNT(*) slots,SUM(status='booked') bookings,
          COALESCE(SUM(CASE WHEN status='booked' THEN price ELSE 0 END),0) recovered_revenue
          FROM slots""").fetchone())
        return {**r,"notice":"Demo database totals, not real market traction."}
