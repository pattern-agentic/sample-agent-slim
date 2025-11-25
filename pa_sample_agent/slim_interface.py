import logging
from pattern_agentic_messaging import PASlimApp, PASlimConfig
from .agent_builder import agent_builder
from .config import settings
from .log_config import configure_logging
from .model import QuestionRequest, StatusRequest, AnswerResponse

configure_logging()
logger = logging.getLogger(__name__)

config = PASlimConfig(
    local_name=settings.slim_local_name,
    endpoint=settings.slim_endpoint,
    auth_secret=settings.slim_auth_secret,
    message_discriminator="type"
)

app = PASlimApp(config)

agent = None


@app.on_session_connect
async def on_connect(session):
    global agent
    if agent is None:
        logger.info("Initializing agent...")
        agent = await agent_builder.create(settings)
        logger.info("Agent initialized successfully")
    logger.info(f"Session {session.session_id} connected")


@app.on_session_disconnect
async def on_disconnect(session):
    logger.info(f"Session {session.session_id} disconnected")


@app.on_message
async def handle_prompt(session, msg: QuestionRequest):
    logger.info(f"Received prompt message: {msg}")

    try:
        response = await agent.ask(msg.prompt)
        await session.send(AnswerResponse(answer=response))
        logger.info("Sent response")
    except Exception as exc:
        logger.error(f"Error processing request: {exc}", exc_info=True)
        await session.send({"type": "error", "error": str(exc)})


@app.on_message
async def handle_status(session, msg: StatusRequest):
    logger.info("Receiedv status request response")
    await session.send({"type": "status-response", "status": "healthy"})


@app.on_message
async def handle_other(session, msg):
    logger.warning(f"Unknown message type: {msg}")
    msg_type = msg.get('type') if isinstance(msg, dict) else None
    await session.send({"type": "error", "error": f"Unknown message type: {msg_type}"})


if __name__ == "__main__":
    logger.info(f"Starting SLIM interface on {settings.slim_endpoint} as {settings.slim_local_name}")
    app.run()
