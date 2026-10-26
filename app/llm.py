import logging

import httpx

from . import memory
from .config import settings

log = logging.getLogger("llm")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
FALLBACK = "Sorry, I'm having trouble right now. Please try again in a bit."


async def reply(user_id: str, text: str) -> str:
    memory.add(user_id, "user", text)
    messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}, *memory.get(user_id)]
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                json={"model": settings.GROQ_MODEL, "messages": messages, "max_tokens": 300},
            )
            r.raise_for_status()
            out = r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log.error("LLM error: %s", e)
        return FALLBACK
    memory.add(user_id, "assistant", out)
    return out[:1000]
