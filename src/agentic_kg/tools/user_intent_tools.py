# WIP
# TODO: experimenting with different tools for user intent that are broader that user goal
#  - kind of graph
#  - graph description
#  - hypothetical questions (to inform graph schema + leveraged for custom retrievers during GraphRAG)
from google.adk.tools import ToolContext

from agentic_kg.domain.user_intent import UserIntent, create_user_intent, validate_user_intent

from .toolset import ToolSet
from .tool_result import tool_success, tool_error

USER_INTENT_KEY = "user_intent_specification"

def set_kind_of_graph(kind_of_graph: str, tool_context: ToolContext):
    """Sets the kind of graph as described by the user.

    The user intent specification will be updated and marked as "proposed".
    
    Args:
        kind_of_graph: 2-3 words indicating the kind of graph, for example "GraphRAG Research" or "Popular Movies"

    Returns:
        
    """
    # get current user intent in session state or create new one
    user_intent = tool_context.state.get(USER_INTENT_KEY, create_user_intent())

    try:
        valid_user_intent = validate_user_intent(user_intent)
        valid_user_intent["kind_of_graph"] = kind_of_graph
        valid_user_intent["status"] = "proposed"
        tool_context.state[USER_INTENT_KEY] = valid_user_intent
        return tool_success(USER_INTENT_KEY, valid_user_intent)
    except Exception as e:
        return tool_error(f"Invalid user intent: {e}")


def set_graph_description(graph_description: str, tool_context: ToolContext):
    """Sets the description of the graph as described.
    
    Args:
        graph_description: a single paragraph description of the graph
    """
    user_intent = tool_context.state.get(USER_INTENT_KEY, create_user_intent())

    try:
        valid_user_intent = validate_user_intent(user_intent)
        valid_user_intent["graph_description"] = graph_description
        tool_context.state[USER_INTENT_KEY] = valid_user_intent
        return tool_success(USER_INTENT_KEY, valid_user_intent)
    except Exception as e:
        return tool_error(f"Invalid user intent: {e}")

def get_user_intent(tool_context: ToolContext):
    """Returns the intent, which is a dictionary containing the kind of graph and its description."""
    if USER_INTENT_KEY not in tool_context.state:
        return tool_error(f"{USER_INTENT_KEY} not set. Ask the user to clarify their intent (kind of graph and description).")  
    
    user_intent_data = tool_context.state.get(USER_INTENT_KEY, create_user_intent())

    return tool_success(USER_INTENT_KEY, user_intent_data)

def approve_user_intent(tool_context: ToolContext):
    """Approves the user intent, changing its status to "approved"."""
    if USER_INTENT_KEY not in tool_context.state:
        return tool_error(f"{USER_INTENT_KEY} not set. Ask the user to clarify their intent (kind of graph and description).")
    
    user_intent_data = tool_context.state.get(USER_INTENT_KEY, create_user_intent())
    user_intent_data["status"] = "approved"
    tool_context.state[USER_INTENT_KEY] = user_intent_data

    return tool_success(USER_INTENT_KEY, tool_context.state[USER_INTENT_KEY])


def reject_user_intent(tool_context: ToolContext):
    """Rejects the user intent, changing its status to "draft"."""
    if USER_INTENT_KEY not in tool_context.state:
        return tool_error(f"{USER_INTENT_KEY} not set. Ask the user to clarify their intent (kind of graph and description).")
    
    user_intent_data = tool_context.state.get(USER_INTENT_KEY, create_user_intent())
    user_intent_data["status"] = "draft"
    tool_context.state[USER_INTENT_KEY] = user_intent_data

    return tool_success(USER_INTENT_KEY, user_intent_data)

def get_approved_user_intent(tool_context: ToolContext):
    """Returns the user's goal, which is a dictionary containing the kind of graph and its description."""
    if USER_INTENT_KEY not in tool_context.state:
        return tool_error(f"{USER_INTENT_KEY} not set. Ask the user to clarify their intent (kind of graph and description).")  
    
    user_intent_data = tool_context.state[USER_INTENT_KEY]

    if user_intent_data["status"] != "approved":
        return tool_error(f"{USER_INTENT_KEY} is not approved. Ask the user to approve their intent.")

    return tool_success(USER_INTENT_KEY, user_intent_data)

toolset = ToolSet(
    name="user_intent_tools",
    description="""User intent tools manage a user intent specification, which is a dictionary with the following components:
    - kind_of_graph: at most 3 words describing the graph, for example "social network" or "USA freight logistics"
    - graph_description: a few sentences about the intention of the graph, for example "A dynamic routing and delivery system for cargo." or "Analysis of product dependencies and supplier alternatives."
    - status: "draft", "proposed", "approved"

    The components can be individually set using specific tool calls. 
    """,
    tools = [
        set_kind_of_graph,
        set_graph_description,
        get_user_intent,
        approve_user_intent,
        reject_user_intent,
        get_approved_user_intent
    ]
)
