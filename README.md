# SLOTLOOP MVP

A runnable prototype for matching flexible customer demand with unused business capacity.

## Run locally
1. Install Python 3.10+ and Node.js 20+.
2. Backend:
   - `cd backend`
   - `python -m pip install -r requirements.txt`
   - `python -m uvicorn app.main:app --reload`
   - API docs: http://127.0.0.1:8000/docs
3. Frontend, in another terminal:
   - `cd frontend`
   - `npm install`
   - `npm run dev`
   - Open http://localhost:5173

If PowerShell blocks virtual-environment activation, skip activation and run `python -m pip ...` directly.

## Docker
From the project root: `docker compose up --build`
Frontend: http://localhost:8080 | API docs: http://localhost:8000/docs

## Demo
Search Haircut around Andheri, book a demo slot, then open Business dashboard to see the booking/revenue metric update. Publish a new slot from the dashboard.

## Data integrity
All seeded businesses, slots, prices and bookings are fictional demo data. No actual customer traction or revenue is claimed. Payments, WhatsApp notifications, maps, production authentication and live business inventory are not connected. The booking endpoint uses a SQLite write transaction and conditional status update to prevent double booking.

## Production work still required
Business verification and consent, authenticated business/customer accounts, payment/refund integration, timezone-aware UTC storage, privacy controls, audit logging, rate limiting, monitoring, backups and real-time inventory synchronization.

## Live Link:
link:https://this-is-yash.github.io/slotloop/
