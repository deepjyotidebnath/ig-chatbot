import hashlib
import hmac
import logging

import httpx

from .config import settings

log = logging.getLogger("instagram")
GRAPH_URL = "https://graph.instagram.com/v21.0/me/messages"


def valid_signature(body: bytes, header: str | None) -> bool:
    if not settings.APP_SECRET:
        return True
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(settings.APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.split("=", 1)[1])


async def send_text(recipient_id: str, text: str) -> None:
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(
            GRAPH_URL,
            headers={"Authorization": f"Bearer {settings.IG_ACCESS_TOKEN}"},
            json={"recipient": {"id": recipient_id}, "message": {"text": text}},
        )
        if r.status_code >= 400:
            log.error("Send failed %s: %s", r.status_code, r.text)
