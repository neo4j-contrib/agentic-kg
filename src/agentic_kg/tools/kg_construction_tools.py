import logging

from google.adk.tools import ToolContext
from typing import Dict, Any, List

from agentic_kg.common.neo4j_for_adk import get_graphdb
from agentic_kg.tools.cypher_tools import create_uniqueness_constraint
from agentic_kg.common.tool_result import tool_success, tool_error

logger = logging.getLogger(__name__)

graphdb = get_graphdb()

APPROVED_CONSTRUCTION_PLAN = "approved_construction_plan"

def construct_node(construction_rule: dict) -> Dict[str, Any]:
    """Construct a node from the construction rule."""
    batch_load_nodes_cypher = """
    LOAD CSV WITH HEADERS FROM "file:///" + $import_file AS row
    MERGE (n:$($label) {id: row[$unique_column_name]})
    SET n += row
    """
    return graphdb.send_query(batch_load_nodes_cypher, {
        "import_file": construction_rule["source_file"],
        "label": construction_rule["label"],
        "unique_column_name": construction_rule["unique_column_name"],
        "properties": construction_rule["properties"]
    })

def construct_relationship(construction_rule: dict) -> Dict[str, Any]:
    """Construct a relationship from the construction rule."""
    batch_load_relationships_cypher = """
    LOAD CSV WITH HEADERS FROM "file:///" + $import_file AS row
    MATCH (from_node:$($from_node_label) {id: row[$from_node_column]})
    MATCH (to_node:$($to_node_label) {id: row[$to_node_column]})
    MERGE (from_node)-[r:$($relationship_type)]->(to_node)
    SET r += row
    """
    return graphdb.send_query(batch_load_relationships_cypher, {
        "import_file": construction_rule["source_file"],
        "from_node_label": construction_rule["from_node_label"],
        "to_node_label": construction_rule["to_node_label"],
        "from_node_column": construction_rule["from_node_column"],
        "to_node_column": construction_rule["to_node_column"],
        "relationship_type": construction_rule["relationship_type"],
        "properties": construction_rule["properties"]
    })


def load_nodes_from_csv(
    source_file: str,
    label: str,
    unique_column_name: str,
    properties: list[str],
) -> Dict[str, Any]:
    """Batch loading of nodes from a CSV file"""

    # load nodes from CSV file by merging on the unique_column_name value
    query = f"""LOAD CSV WITH HEADERS FROM "file:///" + $source_file AS row
    CALL (row) {{
        MERGE (n:$($label) {{ {unique_column_name} : row[$unique_column_name] }})
        FOREACH (k IN $properties | SET n[k] = row[k])
    }} IN TRANSACTIONS OF 1000 ROWS
    """

    results = graphdb.send_query(query, {
        "source_file": source_file,
        "label": label,
        "unique_column_name": unique_column_name,
        "properties": properties
    })
    return results


def import_nodes(node_construction: dict) -> dict:
    """Import nodes as defined by a node construction rule."""

    # create a uniqueness constraint for the unique_column
    uniqueness_result = create_uniqueness_constraint(
        node_construction["label"],
        node_construction["unique_column_name"]
    )

    if (uniqueness_result["status"] == "error"):
        return uniqueness_result

    # import nodes from csv
    load_nodes_result = load_nodes_from_csv(
        node_construction["source_file"],
        node_construction["label"],
        node_construction["unique_column_name"],
        node_construction["properties"]
    )

    return load_nodes_result


def import_relationships(relationship_construction: dict) -> Dict[str, Any]:
    """Import relationships as defined by a relationship construction rule."""

    # load nodes from CSV file by merging on the unique_column_name value 
    from_node_column = relationship_construction["from_node_column"]
    to_node_column = relationship_construction["to_node_column"]
    query = f"""LOAD CSV WITH HEADERS FROM "file:///" + $source_file AS row
    CALL (row) {{
        MATCH (from_node:$($from_node_label) {{ {from_node_column} : row[$from_node_column] }}),
              (to_node:$($to_node_label) {{ {to_node_column} : row[$to_node_column] }} )
        MERGE (from_node)-[r:$($relationship_type)]->(to_node)
        FOREACH (k IN $properties | SET r[k] = row[k])
    }} IN TRANSACTIONS OF 1000 ROWS
    """
    
    results = graphdb.send_query(query, {
        "source_file": relationship_construction["source_file"],
        "from_node_label": relationship_construction["from_node_label"],
        "from_node_column": relationship_construction["from_node_column"],
        "to_node_label": relationship_construction["to_node_label"],
        "to_node_column": relationship_construction["to_node_column"],
        "relationship_type": relationship_construction["relationship_type"],
        "properties": relationship_construction["properties"]
    })
    return results

def construct_domain_graph(construction_plan: dict) -> Dict[str, Any]:
    """Construct a domain graph according to a construction plan."""

    logger.debug(f"Building domain graph from approved construction plan: {construction_plan}")

    # first, import nodes
    node_constructions = [value for value in construction_plan.values() if value['construction_type'] == 'node']
    for node_construction in node_constructions:
        import_nodes(node_construction)

    # second, import relationships
    relationship_constructions = [value for value in construction_plan.values() if value['construction_type'] == 'relationship']
    for relationship_construction in relationship_constructions:
        import_relationships(relationship_construction)

    return tool_success("domain_graph_constructed", construction_plan)

def build_graph_from_construction_rules(tool_context: ToolContext) -> Dict[str, Any]:
    """Build a graph from the approved construction rules."""
    if not APPROVED_CONSTRUCTION_PLAN in tool_context.state:
        return tool_error(f"{APPROVED_CONSTRUCTION_PLAN} not set.")  

    approved_construction_plan = tool_context.state[APPROVED_CONSTRUCTION_PLAN]
    
    return construct_domain_graph(approved_construction_plan)