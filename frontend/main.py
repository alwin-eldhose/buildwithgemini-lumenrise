"""Minimal FastAPI proxy for a deployed A2A agent (Agent Runtime, agents-cli 1.1.0+).

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the
browser). The proxy authenticates with Application Default Credentials and
forwards chat to the deployed agent over the A2A protocol, returning replies as
structured parts the chat UI knows how to show:

  * {"kind": "text", "text": ...}  -> a normal chat bubble
  * {"kind": "a2ui", "data": ...}  -> one A2UI message (beginRendering /
    surfaceUpdate); static/index.html renders these as a card.
"""

import os
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import (
    AgentCard,
    Message,
    Part,
    Role,
)
from google.protobuf.json_format import MessageToDict, ParseDict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ["AGENT_ENGINE_RESOURCE_NAME"]
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"
_A2UI_MIME = "application/json+a2ui"
ROLE_USER = getattr(Role, "ROLE_USER", getattr(Role, "user", "user"))

_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI()


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


_contexts: dict[str, str] = {}
_card: AgentCard | None = None


async def _get_card(client: httpx.AsyncClient) -> AgentCard:
    global _card
    if _card is None:
        resp = await client.get(A2A_CARD_URL)
        resp.raise_for_status()
        data = resp.json()
        try:
            card = ParseDict(data, AgentCard(), ignore_unknown_fields=True)
        except Exception:
            card = AgentCard(**data)
        _card = card
    return _card


def _extract_parts(parts: list) -> list[dict]:
    out: list[dict] = []
    for p in parts:
        if hasattr(p, "DESCRIPTOR"):
            p_dict = MessageToDict(p, preserving_proto_field_name=True)
        elif isinstance(p, dict):
            p_dict = p
        else:
            p_dict = {}

        if "text" in p_dict and p_dict["text"]:
            txt = p_dict["text"].strip()
            # Check for <a2ui-json>...</a2ui-json> or <a2a_datapart_json>...</a2a_datapart_json>
            m = re.search(r"<(?:a2ui-json|a2a_datapart_json)>(.*?)</(?:a2ui-json|a2a_datapart_json)>", txt, re.DOTALL)
            json_str = m.group(1).strip() if m else None
            if not json_str and (txt.startswith("{") or txt.startswith("[")):
                json_str = txt

            if json_str:
                try:
                    data_obj = json.loads(json_str)
                    if isinstance(data_obj, dict) and ("surfaceUpdate" in data_obj or "beginRendering" in data_obj or "components" in data_obj):
                        out.append({"kind": "a2ui", "data": data_obj})
                        continue
                except Exception:
                    pass

            out.append({"kind": "text", "text": txt})
            continue

        data_obj = p_dict.get("data")
        if data_obj and isinstance(data_obj, dict):
            a2ui_body = data_obj.get("data") or data_obj
            out.append({"kind": "a2ui", "data": a2ui_body})
    return out



@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        card = await _get_card(client)
        factory = ClientFactory(ClientConfig(httpx_client=client))
        a2a_client = factory.create(card)

        try:
            part = Part(text=message)
        except Exception:
            from a2a.types import TextPart
            part = Part(root=TextPart(text=message))

        msg = Message(
            message_id=str(uuid.uuid4()),
            role=ROLE_USER,
            parts=[part],
            context_id=_contexts.get(user_id),
        )

        try:
            from a2a.types import SendMessageRequest
            req_obj = SendMessageRequest(message=msg)
        except Exception:
            req_obj = msg

        last_task = None
        got_artifact_update = False
        async for event in a2a_client.send_message(req_obj):
            field = event.WhichOneof("payload") if hasattr(event, "WhichOneof") else None
            if field == "task" and hasattr(event, "task"):
                last_task = event.task
                if event.task.context_id:
                    _contexts[user_id] = event.task.context_id
            elif field == "artifact_update" and hasattr(event, "artifact_update"):
                got_artifact_update = True
                parts.extend(_extract_parts(event.artifact_update.artifact.parts))
            elif isinstance(event, tuple):
                task, update = event
                if getattr(task, "context_id", None):
                    _contexts[user_id] = task.context_id
                if getattr(update, "artifact", None):
                    got_artifact_update = True
                    parts.extend(_extract_parts(update.artifact.parts))

        if not got_artifact_update and last_task is not None:
            for artifact in getattr(last_task, "artifacts", None) or []:
                parts.extend(_extract_parts(artifact.parts))

    if not parts:
        parts = [{"kind": "text", "text": "(The agent didn't return a reply.)"}]
    return JSONResponse({"parts": parts})


app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
