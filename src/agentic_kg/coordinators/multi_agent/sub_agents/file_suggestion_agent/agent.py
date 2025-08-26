from google.adk.agents import Agent, SequentialAgent, LoopAgent


from agentic_kg.common.llm_catalog import get_llm

from .variants import variants

AGENT_NAME = "file_suggestion_agent_v1"
file_suggestion_agent = Agent(
    name=AGENT_NAME,
    description="Helps the user select files to import.",
    model=get_llm(),
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"]
)

root_agent = file_suggestion_agent