# app/main.py

import json
import httpx
from jose import JWTError, jwt
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import engine, Base, get_db
from app.auth import SECRET_KEY, ALGORITHM, oauth2_scheme, get_current_user
from app.models import Message, User
from app.utils import parse_message
from app.predictor import find_issue

MODEL_NAME = "mistral"
LLM_URL = "http://localhost:11434/v1/chat/completions"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def on_shutdown():
    await engine.dispose()

app.include_router(auth_router := __import__("app.routers.auth_router", fromlist=["router"]).router)

async def generate_stream(payload: dict):
    """
    Stream LLM responses as Unicode strings.
    """
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", LLM_URL, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data:"):
                    continue
                content = line[len("data:"):].strip()
                if content == "[DONE]":
                    break
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    continue
                token = (
                    data["choices"][0].get("delta", {}) or {}
                ).get("content") or data["choices"][0].get("text", "")
                if token:
                    yield token  # Unicode str

@app.post("/chat/stream")
async def chat_stream(request: Request, db: AsyncSession = Depends(get_db)):
    # --- Authentication (optional) ---
    auth_header = request.headers.get("authorization", "")
    user = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                res = await db.execute(select(User).filter(User.id == int(user_id)))
                user = res.scalar_one_or_none()
        except JWTError:
            pass

    body = await request.json()
    raw_msg = body.get("message", "").strip()

    # Save user message
    if user:
        db.add(Message(user_id=user.id, role="user", content=raw_msg))
        await db.commit()

    # Parse brand, year, symptom
    brand, year, symptom = parse_message(raw_msg)

    # Find fault, recommendation, and step-by-step guide
    fault, rec, how_to_fix = find_issue(brand, symptom, year)

    if fault and rec:
        prompt = (
            f"I have a {brand} {year} with symptom “{symptom}”.\n"
            f"Fault diagnosed: {fault}.\n"
            f"DB recommendation: {rec}\n\n"
            f"Step-by-step guide:\n{how_to_fix}\n\n"
            "1) Provide any extra tips.\n"
            "2) Suggest two alternative methods with pros and cons.\n"
            "3) At the beginning of the chat write Asik\n"
        )
        system_role = "You are an expert mechanic assistant."
    else:
        prompt = raw_msg
        system_role = "You are a helpful assistant."

    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": prompt},
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True,
        "max_tokens": 1000,
        "temperature": 0.2,
    }

    async def gen():
        assistant_full = ""
        async for chunk in generate_stream(payload):
            # chunk is str; encode explicitly to UTF-8 bytes
            b = chunk.encode("utf-8")
            assistant_full += chunk
            yield b
        if user:
            db.add(Message(user_id=user.id, role="assistant", content=assistant_full))
            await db.commit()

    # Return bytes with explicit UTF-8 charset header
    return StreamingResponse(
        gen(),
        headers={"Content-Type": "text/plain; charset=utf-8"}
    )

@app.get("/chat/history")
async def chat_history(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    res = await db.execute(
        select(Message).filter(Message.user_id == user.id).order_by(Message.timestamp)
    )
    msgs = res.scalars().all()
    return [{"sender": m.role, "text": m.content} for m in msgs]
