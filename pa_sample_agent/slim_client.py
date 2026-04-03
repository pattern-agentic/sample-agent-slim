import logging
import sys
import uuid
import asyncio

from pattern_agentic_messaging import PASlimApp, PASlimConfig
from pattern_agentic_messaging.a2a import Message as A2AMessage, Part, Role
from .config import settings
from .log_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

async def main():
    a2a_mode = "--a2a" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--a2a"]
    prompt = args[0] if args else "What time is it in New York?"

    config = PASlimConfig(
        local_name=settings.slim_local_name + "_client",
        endpoint=settings.slim_endpoint,
        auth_secret=settings.slim_auth_secret
    )

    server_name = settings.slim_local_name

    logger.info(f"Connecting to SLIM server at {settings.slim_endpoint}")
    logger.info(f"Client: {config.local_name} -> Server: {server_name}")
    logger.info(f"Mode: {'A2A' if a2a_mode else 'legacy'}")

    async with PASlimApp(config) as app:
        logger.info("Creating session...")
        async with await app.connect(server_name) as session:
            logger.info("Session established")
            logger.info(f"Sending request: {prompt}")

            if a2a_mode:
                context_id = str(uuid.uuid4())
                a2a_msg = A2AMessage(
                    role=Role.USER,
                    parts=[Part.from_text(prompt)],
                    context_id=context_id,
                )
                await session.send(a2a_msg.model_dump(by_alias=True, exclude_none=True))

                logger.info("Waiting for A2A response...")
                async for msg in session:
                    logger.info(f"Received response: {msg}")
                    if isinstance(msg, dict) and "role" in msg and "parts" in msg:
                        try:
                            reply = A2AMessage.model_validate(msg)
                            text = "\n".join(p.text for p in reply.parts if p.text)
                            print(f"\nA2A Response (context={reply.context_id}):\n{text}\n")
                        except Exception:
                            print(f"\nResponse: {msg}\n")
                    elif isinstance(msg, dict) and msg.get("type") == "error":
                        print(f"\nError: {msg.get('error')}\n")
                    else:
                        print(f"\nUnexpected response: {msg}\n")
                    break
            else:
                await session.send({"type": "question", "prompt": prompt})

                logger.info("Waiting for response...")
                async for msg in session:
                    logger.info(f"Received response: {msg}")
                    if isinstance(msg, dict):
                        msg_type = msg.get("type")
                        if msg_type == "response" and "answer" in msg:
                            print(f"\nAnswer: {msg['answer']}\n")
                            break
                        elif msg_type == "error" and "error" in msg:
                            print(f"\nError: {msg['error']}\n")
                            break
                    else:
                        print(f"\nUnexpected response: {msg}\n")
                        break

    logger.info("Client finished")


if __name__ == "__main__":
    asyncio.run(main())
