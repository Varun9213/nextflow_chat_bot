# backend/server.py
import os
import uuid
import re
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# FastAPI app
APP = FastAPI(title="Docs Q&A Chat - FastAPI")

APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
SESSIONS: Dict[str, List[Dict[str, str]]] = {}

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() in ("1", "true", "yes")

if not MOCK_MODE:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        raise RuntimeError("openai package required in non-mock mode")

# Load docs into memory (.md, .txt, .mf)
DOCS = []
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
if os.path.isdir(DOCS_DIR):
    for fname in os.listdir(DOCS_DIR):
        if fname.endswith((".md", ".txt", ".mf")):
            path = os.path.join(DOCS_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                DOCS.append({"title": fname, "text": f.read()})

# Request/response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    sources: Optional[List[str]] = []

# Simple doc retrieval
def find_docs_for_query(query: str, max_hits=3):
    q = query.lower()
    hits = []
    for doc in DOCS:
        text = doc["text"].lower()
        score = sum(text.count(tok) for tok in re.findall(r"\w+", q))
        if score > 0 or any(tok in text for tok in q.split()):
            hits.append((score, doc))
    hits.sort(reverse=True, key=lambda x: x[0])
    return [h[1]["title"] for h in hits[:max_hits]]

# System prompt
def build_system_prompt():
    return (
        "You are a concise assistant focused on Nextflow documentation Q&A "
        "and light pragmatic troubleshooting. Prioritize doc answers (70%) and "
        "pragmatic steps (30%). If you found docs to cite, mention them in a 'Sources' "
        "section at the end and be explicit about uncertainty. If unknown, suggest how to verify."
    )

# Chat endpoint
@APP.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is empty")

    # Session handling
    session_id = req.session_id or str(uuid.uuid4())
    session_history = SESSIONS.setdefault(session_id, [])

    # Append user message
    session_history.append({"role": "user", "content": message})

    # Retrieval
    sources = find_docs_for_query(message)
    retrieval_note = f"Found relevant docs: {', '.join(sources)}" if sources else ""

    # Mock mode
    if MOCK_MODE:
        reply = f"(MOCK) I received: \"{message}\". {retrieval_note}"
        if "version" in message.lower():
            reply += " Example: check `nextflow -v` locally."
        session_history.append({"role": "assistant", "content": reply})
        return {"reply": reply, "session_id": session_id, "sources": sources}

    # Build messages
    system_prompt = build_system_prompt()
    recent = session_history[-12:]  # limit context
    messages = [{"role": "system", "content": system_prompt}] + recent
    if sources:
        retrieval_text = "Relevant docs: " + "; ".join(sources)
        messages.insert(1, {"role": "system", "content": retrieval_text})

    # Call OpenAI
    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",  # or "gpt-4o-mini" if available
            messages=messages,
            temperature=0.05,
        )
        content = resp.choices[0].message.content
        print(content)
    except Exception as e:
        reply = (
            f"Sorry — I couldn't get an answer from the model. {retrieval_note}. "
            "You can check the docs listed above or try again. (Error logged.)"
        )
        session_history.append({"role": "assistant", "content": reply})
        return {"reply": reply, "session_id": session_id, "sources": sources}

    # Append assistant reply
    session_history.append({"role": "assistant", "content": content})
    return {"reply": content, "session_id": session_id, "sources": sources}
