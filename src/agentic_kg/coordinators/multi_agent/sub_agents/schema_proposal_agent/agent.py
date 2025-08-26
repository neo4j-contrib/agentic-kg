from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext

from google.adk.tools import agent_tool

from typing import AsyncGenerator
from google.adk.events import Event, EventActions

from agentic_kg.common.llm_catalog import get_llm
from agentic_kg.tools.construction_plan_tools import (
    get_proposed_construction_plan, 
    approve_proposed_construction_plan,
)
from agentic_kg.tools.adk_tools import finished

from .variants import variants

# initialize context for schema_proposal_agent with blank feedback, which may get filled later by the schema_critic_agent
def initialize_feedback(callback_context: CallbackContext) -> None:
    callback_context.state["feedback"] = ""

def initialize_schema_and_construction_plan(callback_context: CallbackContext) -> None:
    callback_context.state["proposed_schema"] = ""
    callback_context.state["proposed_construction_plan"] = []

AGENT_NAME = "schema_proposal_agent_v1"
schema_proposal_agent = LlmAgent(
    name=AGENT_NAME,
    description="Proposes a knowledge graph schema based on the user goal and approved file list",
    model=get_llm(),
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
    before_agent_callback=initialize_feedback
)
    
CRITIC_NAME = "schema_critic_agent_v1"
schema_critic_agent = LlmAgent(
    name=CRITIC_NAME,
    description="Criticizes the proposed construction plan for relevance and correctness.",
    model=get_llm(),
    instruction=variants[CRITIC_NAME]["instruction"],
    tools=variants[CRITIC_NAME]["tools"], 
    output_key="feedback"
)

class CheckStatusAndEscalate(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        feedback = ctx.session.state.get("feedback", "valid")
        should_stop = (feedback == "valid")
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))

refinement_loop = LoopAgent(
    name="schema_refinement_loop",
    description="Analyzes approved files to propose a graph construction plan based on user intent and feedback",
    max_iterations=2,
    sub_agents=[schema_proposal_agent, schema_critic_agent, CheckStatusAndEscalate(name="StopChecker")],
    # before_agent_callback=initialize_schema_and_construction_plan
)

root_agent = LlmAgent(
    name="schema_proposal_agent_coordinator",
    model=get_llm(),
    instruction="""
    You are a coordinator for the graph construction plan process. Use tools to propose a schema to the user.
    If the user disapproves, use the tools to refine the schema and ask the user to approve again.
    If the user approves, use the 'approve_proposed_schema' tool to record the approval.
    When the schema approval has been recorded, use the 'finished' tool.

    Guidance for tool use:
    - Use the 'schema_refinement_loop' tool to produce or update a construction plan. 
    - Use the 'get_proposed_construction_plan' tool to get the construction rules for transforming approved files into the schema
    - Present the proposed construction plan to the user for approval
    - If they disapprove, consider their feedback and go back to step 1
    - If the user approves, use the 'approve_proposed_schema' tool and the 'approve_proposed_construction_plan' tool to record the approval
    - Finally, use the 'finished' tool to signal that schema proposal is complete and construction can begin
    """,
    tools=[agent_tool.AgentTool(refinement_loop), 
        get_proposed_construction_plan, 
        approve_proposed_construction_plan,
        finished
    ]
)