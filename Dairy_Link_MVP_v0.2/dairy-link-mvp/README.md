# Dairy Link MVP v0.2

This package extends the Dairy Link starter with working MVP workflows:
- Farmer registration
- Animal registration
- Milk collection (morning/evening)
- Weekly payment calculation and payment records
- Dashboard summaries
- PostgreSQL persistence
- React + TypeScript frontend
- FastAPI backend

## Run

### 1. Database
```bash
docker compose up -d db
```

### 2. Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend docs: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## Important
This is a development MVP, not a production deployment. Authentication,
offline synchronization, M-Pesa automation, GIS, audit hardening, migrations,
and AI are intentionally separate next-stage modules.
