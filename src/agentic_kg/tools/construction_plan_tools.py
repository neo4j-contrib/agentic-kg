from google.adk.tools import ToolContext
from typing import Dict, Any

from agentic_kg.common.neo4j_for_adk import get_graphdb
from agentic_kg.common.tool_result import tool_success, tool_error

graphdb = get_graphdb()

from .file_tools import search_file

PROPOSED_CONSTRUCTION_PLAN = "proposed_construction_plan"
APPROVED_CONSTRUCTION_PLAN = "approved_construction_plan"

#  Tool: Propose Node Construction

NODE_CONSTRUCTION = "node_construction"

def propose_node_construction(approved_file: str, proposed_label: str, unique_column_name: str, proposed_properties: list[str], tool_context:ToolContext) -> dict:
    """Propose a node construction for an approved file that supports the user goal.

    The construction will be added to the proposed construction plan dictionary under using proposed_label as the key.

    The construction entry will be a dictionary with the following keys:
    - construction_type: "node"
    - source_file: the approved file to propose a node construction for
    - label: the proposed label of the node
    - unique_column_name: the name of the column that will be used to uniquely identify constructed nodes
    - properties: A list of property names for the node, derived from column names in the approved file

    Args:
        approved_file: The approved file to propose a node construction for
        proposed_label: The proposed label for constructed nodes (used as key in the construction plan)
        unique_column_name: The name of the column that will be used to uniquely identify constructed nodes

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a "node_construction" key with the construction plan for the node
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    # quick sanity check -- does the approved file have the unique column?
    search_results = search_file(approved_file, unique_column_name)
    if search_results["status"] == "error":
        return search_results # return the error
    if search_results["search_results"]["metadata"]["lines_found"] == 0:
        return tool_error(f"{approved_file} does not have the column {unique_column_name}. Check the file content and try again.")

    # get the current construction plan, or an empty one if none exists
    construction_plan = tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN, {})
    node_construction_rule = {
        "construction_type": "node",
        "source_file": approved_file,
        "label": proposed_label,
        "unique_column_name": unique_column_name,
        "properties": proposed_properties
    }   
    construction_plan[proposed_label] = node_construction_rule
    tool_context.state[PROPOSED_CONSTRUCTION_PLAN] = construction_plan
    return tool_success(NODE_CONSTRUCTION, node_construction_rule)

# Tool: Remove Node Construction
def remove_node_construction(node_label: str, tool_context:ToolContext) -> dict:
    """Remove a node construction from the proposed construction plan based on label.

    Args:
        node_label: The label of the node construction to remove
        tool_context: The tool context

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a 'node_construction_removed' key with the label of the removed node construction
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    construction_plan = tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN, {})
    if node_label not in construction_plan:
       return tool_success("node construction rule not found. removal not needed.")

    del construction_plan[node_label]

    tool_context.state[PROPOSED_CONSTRUCTION_PLAN] = construction_plan
    return tool_success("node_construction_removed", node_label)

#  Tool: Propose Relationship Construction

RELATIONSHIP_CONSTRUCTION = "relationship_construction"

def propose_relationship_construction(approved_file: str, proposed_relationship_type: str, 
    from_node_label: str,from_node_column: str, to_node_label:str, to_node_column: str, 
    proposed_properties: list[str], 
    tool_context:ToolContext) -> dict:
    """Propose a relationship construction for an approved file that supports the user goal.

    The construction will be added to the proposed construction plan dictionary under using proposed_relationship_type as the key.

    Args:
        approved_file: The approved file to propose a node construction for
        proposed_relationship_type: The proposed label for constructed relationships
        from_node_label: The label of the source node
        from_node_column: The name of the column within the approved file that will be used to uniquely identify source nodes
        to_node_label: The label of the target node
        to_node_column: The name of the column within the approved file that will be used to uniquely identify target nodes
        unique_column_name: The name of the column that will be used to uniquely identify target nodes

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a "relationship_construction" key with the construction plan for the node
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    # quick sanity check -- does the approved file have the from_node_column?
    search_results = search_file(approved_file, from_node_column)
    if search_results["status"] == "error": 
      return search_results  # return the error if there is one
    if search_results["search_results"]["metadata"]["lines_found"] == 0:
        return tool_error(f"{approved_file} does not have the from node column {from_node_column}. Check the content of the file and reconsider the relationship.")

    # quick sanity check -- does the approved file have the to_node_column?
    search_results = search_file(approved_file, to_node_column)
    if search_results["status"] == "error" or search_results["search_results"]["metadata"]["lines_found"] == 0:
        return tool_error(f"{approved_file} does not have the to node column {to_node_column}. Check the content of the file and reconsider the relationship.")

    construction_plan = tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN, {})
    relationship_construction_rule = {
        "construction_type": "relationship",
        "source_file": approved_file,
        "relationship_type": proposed_relationship_type,
        "from_node_label": from_node_label,
        "from_node_column": from_node_column,
        "to_node_label": to_node_label,
        "to_node_column": to_node_column,
        "properties": proposed_properties
    }   
    construction_plan[proposed_relationship_type] = relationship_construction_rule
    tool_context.state[PROPOSED_CONSTRUCTION_PLAN] = construction_plan
    return tool_success(RELATIONSHIP_CONSTRUCTION, relationship_construction_rule)

# Tool: Remove Relationship Construction
def remove_relationship_construction(relationship_type: str, tool_context:ToolContext) -> dict:
    """Remove a relationship construction from the proposed construction plan based on type.

    Args:
        relationship_type: The type of the relationship construction to remove
        tool_context: The tool context

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a 'relationship_construction_removed' key with the type of the removed relationship construction
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    construction_plan = tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN, {})

    if relationship_type not in construction_plan:
        return tool_success("relationship_construction_removed", "relationship construction rule not found. removal not needed.")
    
    construction_plan.pop(relationship_type)
    
    tool_context.state[PROPOSED_CONSTRUCTION_PLAN] = construction_plan
    return tool_success("relationship_construction_removed", relationship_type) 


# Tool: Approve the proposed construction plan
def approve_proposed_construction_plan(tool_context:ToolContext) -> dict:
    """Approve the proposed construction plan."""
    tool_context.state[APPROVED_CONSTRUCTION_PLAN] = tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN)
    return tool_success(APPROVED_CONSTRUCTION_PLAN, tool_context.state[APPROVED_CONSTRUCTION_PLAN])

# Tool: Get Proposed construction Plan

def get_proposed_construction_plan(tool_context:ToolContext) -> dict:
    """Get the proposed construction plan."""
    return tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN, [])


def get_approved_construction_plan(tool_context:ToolContext) -> dict:
    """Get the approved construction plan."""
    return tool_context.state.get(APPROVED_CONSTRUCTION_PLAN, [])