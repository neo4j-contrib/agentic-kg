from google.adk.agents import Agent

from agentic_kg.common.llm_catalog import get_llm

# variants are pairs of instructions with tools
from .variants import variants

AGENT_NAME = "graph_construction_agent_v1"
graph_construction_agent = Agent(
        name=AGENT_NAME,
        model=get_llm(),
        description="Knowledge graph construction based on approved construction rules.", 
        instruction=variants[AGENT_NAME]["instruction"],
        tools=variants[AGENT_NAME]["tools"]
    )

root_agent = graph_construction_agent