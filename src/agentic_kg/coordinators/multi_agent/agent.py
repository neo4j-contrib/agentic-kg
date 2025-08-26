from google.adk.agents import LlmAgent

from agentic_kg.common.llm_catalog import get_llm
from agentic_kg.tools.cypher_tools import get_physical_schema

from .sub_agents import user_intent_agent, file_suggestion_agent, schema_proposal_agent, graph_construction_agent, graphrag_agent


full_workflow_agent = LlmAgent(
    name="kg_construction_agent_v1",
    description="""Knowledge graph construction using Neo4j.""",
    model=get_llm(),
    instruction="""You are an expert in knowledge graph construction using Neo4j.
        Your primary goal is to guide the user through the process of knowledge graph construction.

        Delegate to sub-agents to perform the work. Follow this sequence of agents:
        1. user_intent_agent -- start here to determine the user goal for kind of graph and description
        2. file_suggestion_agent -- requires approved user goals to make suggestions about what files to use
        3. schema_proposal_agent -- requires approved file suggestions to propose a graph schema with construction rules
        4. graph_construction_agent -- requires an approved graph schema design
        5. graphrag_agent -- used to interact with the knowledge graph.only available if 'get_physical_schema' tool shows that a graph exists
        """,
    sub_agents=[
        user_intent_agent, 
        file_suggestion_agent, 
        schema_proposal_agent, 
        graph_construction_agent,
        graphrag_agent
    ],
    tools=[
        get_physical_schema
    ]
)

root_agent = full_workflow_agent