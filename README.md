# GigBridge

A professional network and gig-booking platform for independent musicians, bands, and club venues.

**Musicians** showcase profiles with genres, instruments, experience, and demo clips. They can create a band page (size, members, open positions) or discover and join bands that are recruiting.

**Venues** post gig requirements (date, genre, budget, band size), browse and shortlist bands, and manage the full booking pipeline: applied, shortlisted, confirmed, completed, reviewed.

## Architecture

Modular monolith: one FastAPI application with strict module boundaries, deployed as a single container. Modules communicate only through each other's service layer, never by touching another module's tables. This keeps the MVP simple to build, debug, and deploy while making later extraction into services mechanical if scale demands it.

```
React (Vite) SPA  ->  FastAPI modular monolith  ->  PostgreSQL / Redis / S3
                          |-- profiles
                          |-- bands
                          |-- gigs
                          |-- bookings
                          |-- chat
                          |-- matching
```

## Tech stack

| Layer      | Choice                          |
|------------|---------------------------------|
| Frontend   | React 18 + Vite + Tailwind CSS  |
| Backend    | Python 3.12 + FastAPI           |
| Database   | PostgreSQL (+ pgvector later)   |
| Cache/queue| Redis                           |
| Media      | Amazon S3 + CloudFront          |
| Deploy     | Docker on AWS ECS/EC2           |

## Local development

```bash
# 1. Start Postgres + Redis
docker compose up -d db redis

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# 3. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

API docs are auto-generated at http://localhost:8000/docs

## Roadmap

- **Phase 1 — Foundation**: auth + roles, musician profiles, media upload, band pages
- **Phase 2 — Networking**: discovery feed, vacancies and join requests, messaging
- **Phase 3 — Booking engine**: venue accounts, gig postings, booking workflow, reviews
- **Phase 4 — Scale**: pgvector matching, React Native app, payments, analytics
