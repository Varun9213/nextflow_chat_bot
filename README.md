# Docs Q&A Chat Assistant

Demo: https://YOUR_DEPLOY_URL

## Goal
A small chat assistant for documentation Q&A (Nextflow-focused) + light troubleshooting.

## Local setup

### Backend
1. cd backend
2. python -m venv .venv
3. source .venv/bin/activate
4. pip install -r requirements.txt
5. Create `.env` file and fill in:
   - OPENAI_API_KEY=sk-...
   - MOCK_MODE=false  # set true to run demo without API key
6. uvicorn server:APP --reload --port 5000

### Frontend
1. cd frontend
2. npm install
3. npm run dev
4. Open http://localhost:5173

The frontend is configured with Vite proxy so calls to `/chat` are proxied to `http://localhost:5000`.

## Deploy
You can deploy backend (Docker) to Render / Railway / Fly / Cloud Run.
- Build command: (for Docker) use the provided `backend/Dockerfile`
- Set environment variables on the host: `OPENAI_API_KEY` and `MOCK_MODE` (optional)
Frontend can be deployed to Vercel (static build) and the backend to Render; or deploy both in one service via Docker.

## API
POST /chat
Body: `{ "message": "...", "session_id": "optional-uuid" }`
Response: `{ "reply": "...", "session_id": "...", "sources": ["doc1.md"] }`

## Notes
- Sessions stored in-memory (no persistence).
- Mock mode is provided when you don't want to expose API keys for demo.
- Basic retrieval implemented from `backend/docs/`.

