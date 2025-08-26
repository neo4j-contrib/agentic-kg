from google.adk.agents import Agent

from agentic_kg.common.llm_catalog import get_llm

from .variants import variants

AGENT_NAME = "file_suggestion_agent_v3"

file_suggestion_agent = Agent(
    name=AGENT_NAME,
    description="Criticize the file list for relevance to the kind of graph indicated by the 'kind_of_graph' key in session state.",
    model=get_llm(LlmKind.reasoning),
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"]
)

root_agent = file_suggestion_agent