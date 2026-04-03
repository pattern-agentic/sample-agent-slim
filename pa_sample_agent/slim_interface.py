import logging
from pattern_agentic_messaging import PatternAgentSessionToken
from pattern_agentic_messaging.a2a import Message as A2AMessage, Part, Role
from pattern_agent_sdk import pa_sdk
from .agent_builder import agent_builder
from .config import settings
from .log_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = pa_sdk.agent_app()

agent = None


@app.on_init
async def on_init():
    settings.watch_env_file()


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
async def handle_a2a(session, msg: A2AMessage, agent_session: PatternAgentSessionToken):
    logger.info(f"Session token: session_id={agent_session.session_id} tenant={agent_session.tenant_id} user={agent_session.user_id} agents={agent_session.agents}")
    text_parts = [p.text for p in msg.parts if p.text is not None]
    if not text_parts:
        logger.warning("A2A message has no text parts")
        await session.send({"type": "error", "error": "A2A message contains no text parts"})
        return

    prompt = "\n".join(text_parts)
    logger.info(f"Received A2A message (context={msg.context_id}): {prompt[:100]}")

    system_prompt = await pa_sdk.prompt("inference")
    response = await agent.ask(prompt, system_prompt=system_prompt)

    reply = A2AMessage(
        role=Role.AGENT,
        parts=[Part.from_text(response)],
        context_id=msg.context_id,
        task_id=msg.task_id,
    )
    await session.send(reply.model_dump(by_alias=True, exclude_none=True))
    logger.info(f"Sent A2A response (context={msg.context_id})")


@app.on_message
async def handle_other(session, msg):
    logger.warning(f"Unknown message type: {msg}")
    msg_type = msg.get('type') if isinstance(msg, dict) else None
    await session.send({"type": "error", "error": f"Unknown message type: {msg_type}"})


if __name__ == "__main__":
    app.run()
