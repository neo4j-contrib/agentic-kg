from .common.config import validate_env
from .agents.user_intent_agent.agent import build_user_intent_agent

root_agent = build_user_intent_agent()
