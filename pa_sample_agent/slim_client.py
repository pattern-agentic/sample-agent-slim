import sys
import asyncio
import logging
from pattern_agentic_messaging import PASlimApp, PASlimConfig
from .config import settings

logger = logging.getLogger(__name__)



async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    config = PASlimConfig(
        local_name=settings.slim_local_name + "_client",
        endpoint=settings.slim_endpoint,
        auth_secret=settings.slim_auth_secret
    )

    server_name = settings.slim_local_name

    logger.info(f"Connecting to SLIM server at {settings.slim_endpoint}")
    logger.info(f"Client: {config.local_name} -> Server: {server_name}")

    async with PASlimApp(config) as app:
        logger.info("Creating session...")
        async with await app.connect(server_name) as session:
            logger.info("Session established")

            prompt = sys.argv[1] if len(sys.argv) >= 2 else "What time is it in New York?"
            logger.info(f"Sending request: {prompt}")

            await session.send({"type": "question", "prompt": prompt})

            logger.info("Waiting for response...")
            async for msg in session:
                logger.info(f"Received response: {msg}")

                if isinstance(msg, dict):
                    msg_type = msg.get("type")
                    if msg_type in {"response", "answer"} and "answer" in msg:
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
