from typing import TypedDict, Literal, Any, TypeGuard
from pydantic import TypeAdapter, ValidationError

class UserIntent(TypedDict):
    """Specifies a user's intent for graph construction, retrieval and management.
    
    Attributes:
        kind_of_graph: A 2-3 word definition of the kind of graph (e.g., "recent US patents")
        graph_description: A detailed description of the graph, summarizing the user's intent
        status: The current status of the user intent
    """
    kind_of_graph: str | None
    graph_description: str | None
    status: Literal["proposed", "approved"]

# Create a TypeAdapter for runtime validation
UserIntentAdapter = TypeAdapter(UserIntent)

def create_user_intent(
    kind_of_graph: str | None = None,
    graph_description: str | None = None,
    status: Literal["proposed", "approved"] = "proposed"
) -> UserIntent:
    """Create and validate a UserIntent dictionary.
    
    Args:
        kind_of_graph: A 2-3 word definition of the graph type
        graph_description: Detailed description of the graph
        status: Current status of the intent (defaults to "proposed")
        
    Returns:
        A validated UserIntent dictionary
        
    Raises:
        pydantic.ValidationError: If the input doesn't match the UserIntent schema
    """
    intent = {
        "kind_of_graph": kind_of_graph,
        "graph_description": graph_description,
        "status": status
    }
    return UserIntentAdapter.validate_python(intent)

def validate_user_intent(data: Any) -> UserIntent:
    """Validate raw data against the UserIntent schema.
    
    Args:
        data: The data to validate (dict, JSON string, etc.)
        
    Returns:
        Validated UserIntent dictionary
        
    Raises:
        pydantic.ValidationError: If validation fails
    """
    return UserIntentAdapter.validate_python(data)

def is_valid_user_intent(data: Any) -> TypeGuard[UserIntent]:
    """Check if data is a valid UserIntent without raising an exception.
    
    Args:
        data: The data to validate
        
    Returns:
        bool: True if data is a valid UserIntent, False otherwise
    """
    try:
        UserIntentAdapter.validate_python(data)
        return True
    except (ValidationError, TypeError, ValueError):
        return False
