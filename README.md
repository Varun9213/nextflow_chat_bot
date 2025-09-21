# Docs Q&A Chat Assistant

Demo: https://nextflow-chat-bot.vercel.app/

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

## API
POST /chat
Body: `{ "message": "...", "session_id": "optional-uuid" }`
Response: `{ "reply": "...", "session_id": "...", "sources": ["doc1.md"] }`

## Architecture Overview

        ┌──────────────┐
        │   User/Browser  │
        └──────────────┘
                │
                ▼
       [Nextflow Chat Bot Frontend]
        (Hosted on Vercel)
                │
                │ Fetch API requests
                ▼
       [FastAPI Backend API]
        (Hosted on Render)
                │
                │ Calls OpenAI API / handles logic
                ▼
          [OpenAI API]



- **Frontend:** Deployed on [Vercel](https://nextflow-chat-bot.vercel.app)  
  - Built with Vite + React  
  - Handles the chat UI and sends user messages to the backend

- **Backend:** Deployed on [Render](https://nextflow-backend.onrender.com)  
  - Built with FastAPI and Docker  
  - Receives messages from the frontend, calls the OpenAI API, and returns bot responses

- **Flow:**  
  1. User sends a message on the frontend  
  2. Frontend calls Render backend API  
  3. Backend processes the request and calls OpenAI  
  4. Backend returns the response to the frontend  
  5. Frontend displays the bot’s reply



## Notes
- Sessions stored in-memory (no persistence).
- Mock mode is provided when you don't want to expose API keys for demo.
- Basic retrieval implemented from `backend/docs/`.
- Backend deployed on render and frontend deployed on vercel

