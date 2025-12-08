import asyncio
import json
import logging
import sys

from agntcy_app_sdk.factory import AgntcyFactory
from agntcy_app_sdk.semantic.message import Message

from .config import settings
from .log_config import configure_logging

logger = logging.getLogger(__name__)


async def main():
    configure_logging()

    factory = AgntcyFactory()
    transport = factory.create_transport(
        "SLIM",
        endpoint=settings.slim_endpoint,
        name=f"{settings.slim_local_name}_client",
        shared_secret_identity=settings.slim_auth_secret,
    )

    await transport.setup()

    prompt = sys.argv[1] if len(sys.argv) >= 2 else "What time is it in New York?"
    logger.info(
        "Connecting to SLIM at %s | client=%s -> server=%s",
        settings.slim_endpoint,
        f"{settings.slim_local_name}_client",
        settings.slim_local_name,
    )

    try:
        response = await transport.request(
            recipient=settings.slim_local_name,
            message=Message(
                type="application/json",
                payload=json.dumps({"type": "question", "prompt": prompt}),
            ),
            timeout=30,
        )
    finally:
        await transport.close()

    if not response:
        print("\nNo response received.\n")
        return

    try:
        raw = response.payload.decode("utf-8") if isinstance(response.payload, (bytes, bytearray)) else response.payload
        body = json.loads(raw) if isinstance(raw, str) else raw
    except Exception as exc:
        print(f"\nError parsing response: {exc}\n")
        return

    if isinstance(body, dict) and "answer" in body:
        print(f"\nAnswer: {body['answer']}\n")
    elif isinstance(body, dict) and "error" in body:
        print(f"\nError: {body['error']}\n")
    else:
        print(f"\nUnexpected response: {body}\n")

    logger.info("Client finished")


if __name__ == "__main__":
    asyncio.run(main())
