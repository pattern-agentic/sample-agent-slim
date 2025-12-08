import asyncio
import json
import logging
from typing import Any, Dict

from agntcy_app_sdk.factory import AgntcyFactory
from agntcy_app_sdk.semantic.message import Message

from .agent_builder import agent_builder
from .config import settings
from .log_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

_agent = None
_agent_lock = asyncio.Lock()


async def _get_agent():
    global _agent
    if _agent is None:
        async with _agent_lock:
            if _agent is None:
                logger.info("Initializing agent...")
                _agent = await agent_builder.create(settings)
                logger.info("Agent initialized successfully")
    return _agent


def _parse_payload(message: Message) -> Dict[str, Any]:
    raw = message.payload
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if isinstance(raw, str):
        return json.loads(raw)
    if isinstance(raw, dict):
        return raw
    raise ValueError("Unsupported payload format")


async def handle_message(message: Message) -> Message:
    try:
        body = _parse_payload(message)
    except Exception as exc:
        logger.error(f"Failed to parse incoming message: {exc}", exc_info=True)
        return Message(
            type="application/json",
            payload=json.dumps({"type": "error", "error": "invalid payload"}),
        )

    if not isinstance(body, dict):
        return Message(
            type="application/json",
            payload=json.dumps({"type": "error", "error": "invalid payload"}),
        )

    msg_type = body.get("type")

    if msg_type == "question":
        prompt = body.get("prompt", "")
        agent = await _get_agent()
        try:
            answer = await agent.ask(prompt)
            payload = {"type": "answer", "answer": answer}
        except Exception as exc:
            logger.error(f"Error processing request: {exc}", exc_info=True)
            payload = {"type": "error", "error": str(exc)}
    elif msg_type == "status":
        payload = {"type": "status-response", "status": "healthy"}
    else:
        payload = {"type": "error", "error": f"Unknown message type: {msg_type}"}

    return Message(type="application/json", payload=json.dumps(payload))


async def main():
    factory = AgntcyFactory()
    transport = factory.create_transport(
        "SLIM",
        endpoint=settings.slim_endpoint,
        name=settings.slim_local_name,
        shared_secret_identity=settings.slim_auth_secret,
    )

    await transport.setup()
    transport.set_callback(handle_message)
    # SLIM does not require explicit subscribe, but keeping the call aligns with the interface.
    await transport.subscribe(settings.slim_local_name)

    logger.info(
        "SLIM interface started at %s as %s", settings.slim_endpoint, settings.slim_local_name
    )

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("Shutdown requested, closing transport...")
    finally:
        await transport.close()
        logger.info("Transport closed")


if __name__ == "__main__":
    asyncio.run(main())
