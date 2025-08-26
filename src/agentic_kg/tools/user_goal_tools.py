from google.adk.tools import ToolContext

from agentic_kg.common.neo4j_for_adk import get_graphdb
from agentic_kg.common.tool_result import tool_success, tool_error

graphdb = get_graphdb()

def set_user_goal(kind_of_graph: str, graph_description:str, tool_context: ToolContext):
    """Sets the user's goal, including the kind of graph and its description.
    
    Args:
        kind_of_graph: 2-3 word definition of the kind of graph, for example "recent US patents"
        graph_description: a single paragraph description of the graph, summarizing the user's intent
    """
    user_goal_data = {"kind_of_graph": kind_of_graph, "graph_description": graph_description}
    tool_context.state["user_goal"] = user_goal_data
    tool_context.state["user_goal_approved"] = True
    return tool_success("user_goal", user_goal_data)

def get_user_goal(tool_context: ToolContext):
    """Returns the user's goal, which is a dictionary containing the kind of graph and its description."""
    if "user_goal" not in tool_context.state:
        return tool_error("user_goal not set. Ask the user to clarify their goal (kind of graph and description).")  
    
    user_goal_data = tool_context.state["user_goal"]

    return tool_success("user_goal", user_goal_data)

#  Define the tools for the User Intent Agent

def set_perceived_user_goal(kind_of_graph: str, graph_description:str, tool_context: ToolContext):
    """Sets the user's goal, including the kind of graph and its description.
    
    Args:
        kind_of_graph: 2-3 word definition of the kind of graph, for example "recent US patents"
        graph_description: a single paragraph description of the graph, summarizing the user's intent
    """
    user_goal_data = {"kind_of_graph": kind_of_graph, "graph_description": graph_description}
    tool_context.state["perceived_user_goal"] = user_goal_data
    print("User's goal set:", user_goal_data)
    return tool_success("perceived_user_goal", user_goal_data)

APPROVED_USER_GOAL = "approved_user_goal"

def approve_perceived_user_goal(tool_context: ToolContext):
    """Approves the user's goal, including the kind of graph and its description."""
    if "perceived_user_goal" not in tool_context.state:
        return tool_error("perceived_user_goal not set. Ask the user to clarify their goal (kind of graph and description).")
    
    tool_context.state[APPROVED_USER_GOAL] = tool_context.state["perceived_user_goal"]

    return tool_success(APPROVED_USER_GOAL, tool_context.state[APPROVED_USER_GOAL])

def get_approved_user_goal(tool_context: ToolContext):
    """Returns the user's goal, which is a dictionary containing the kind of graph and its description."""
    if "approved_user_goal" not in tool_context.state:
        return tool_error("approved_user_goal not set. Either delegate to an appropriate agent, or ask the user to clarify their goal if that is your job.")  
    
    user_goal_data = tool_context.state[APPROVED_USER_GOAL]

    return tool_success(APPROVED_USER_GOAL, user_goal_data)


def extend_approved_user_goal(additional_goal: str, tool_context: ToolContext):
    """Extends the user's goal with additional information describing the purpose of the graph."""
    if APPROVED_USER_GOAL not in tool_context.state:
        return tool_error("approved_user_goal not set. Ask the user to clarify their goal (kind of graph and description).")  
    
    user_goal_data = tool_context.state[APPROVED_USER_GOAL]
    extended_user_goal_data = {
        "kind_of_graph": user_goal_data["kind_of_graph"],
        "graph_description": user_goal_data["graph_description"] +"\n" + additional_goal
    }
    tool_context.state[APPROVED_USER_GOAL] = extended_user_goal_data
    return tool_success(APPROVED_USER_GOAL, extended_user_goal_data)