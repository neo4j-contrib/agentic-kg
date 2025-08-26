from google.adk.agents import Agent

from agentic_kg.common.llm_catalog import get_llm, LlmKind

# variants are pairs of instructions with tools
from .variants import variants

AGENT_NAME = "user_intent_agent_v1"

def build_user_intent_agent() -> Agent:
    return Agent(
        name=AGENT_NAME,
        model=get_llm(LlmKind.reasoning),
        description="Knowledge graph use case ideation.",
        instruction=variants[AGENT_NAME]["instruction"],
        tools=variants[AGENT_NAME]["tools"],
    )

# For compatibility with ADK CLI (`adk run path/to/agent_folder` expects a
# module-level `root_agent`). Importing this module directly will construct the
# agent, but the package no longer imports this by default, so general imports
# remain side-effect free.
root_agent = build_user_intent_agent()