import logging

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from . import instagram, llm, memory
from .config import settings

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Instagram Free Chatbot")


async def handle_event(event: dict) -> None:
    sender = event.get("sender", {}).get("id")
    message = event.get("message", {})
    if not sender or message.get("is_echo") or memory.is_duplicate(message.get("mid")):
        return

    text = (message.get("text") or "").strip()
    if not text:
        await instagram.send_text(sender, "I can only read text messages for now 🙂")
        return
    if text.lower() in {"/reset", "reset"}:
        memory.reset(sender)
        await instagram.send_text(sender, "Conversation reset ✅")
        return
    if memory.rate_limited(sender):
        await instagram.send_text(sender, "You're sending messages too fast. Please wait a minute.")
        return

    await instagram.send_text(sender, await llm.reply(sender, text))


@app.get("/webhook")
async def verify(request: Request):
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and p.get("hub.verify_token") == settings.VERIFY_TOKEN:
        return PlainTextResponse(p.get("hub.challenge", ""))
    raise HTTPException(403, "Verification failed")


@app.post("/webhook")
async def webhook(request: Request, background: BackgroundTasks):
    body = await request.body()
    if not instagram.valid_signature(body, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(403, "Bad signature")
    for entry in (await request.json()).get("entry", []):
        for event in entry.get("messaging", []):
            background.add_task(handle_event, event)
    return {"status": "ok"}


@app.get("/")
async def health():
    return {"status": "running"}
