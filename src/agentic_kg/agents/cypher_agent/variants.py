
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the cypher agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""
from agentic_kg.tools.cypher_tools import (
    neo4j_is_ready, 
    get_physical_schema, 
    read_neo4j_cypher,
    write_neo4j_cypher,
    reset_neo4j_data,
    create_uniqueness_constraint,
    merge_node_into_graph
)
from agentic_kg.tools.adk_tools import finished

variants = {

    # cypher_agent_v1
    # first version as a sub-agent, lacking any approval workflow so may go a bit wild
    "cypher_agent_v1": {
        "instruction": """
        You are an expert in Neo4j's Cypher query language and property graphs.
        Your primary goal is to help the user interact with a Neo4j database
        through Cypher queries.

        In addition to reading and writing graph data with Cypher, 
        you have specialized tools for performing additional tasks
        like getting various Neo4j configuration and settings.
        Prefer using a specialized tool over writing Cypher queries.

        For any other user interactions, use the finished tool to defer back to a parent.
        """,
        "tools": [
            neo4j_is_ready, 
            reset_neo4j_data,
            get_physical_schema, 
            read_neo4j_cypher,
            write_neo4j_cypher,
            create_uniqueness_constraint,
            finished
        ]
    },

    # cypher_agent_v2
    # second version, with approval workflow for a collaborative workflow
    # benefits:
    # - collaborative workflow
    # challenges:
    # - may be inconsistent with the schema
    "cypher_agent_v2": {
        "instruction": """
        You are a sub-agent in a larger multi-agent system. 

        Your expertise is in Neo4j's Cypher query language and property graphs.
        Your primary goal is to help the user interact with a Neo4j database
        through Cypher queries.

        In addition to reading and writing graph data with Cypher, 
        you have specialized tools for performing additional tasks
        like getting various Neo4j configuration and settings.
        Prefer using a specialized tool over writing Cypher queries.

        When constructing an example graph with mock data, 
        always design a simple schema that is easy to understand.
        Use a small number of nodes and relationships.

        When constructing a graph from files always follow these steps:
        1. analyze the data sources. how are they related?
        2. design a physical graph schema that fits the available data and the user's goal
        3. create appropriate constraints for nodes with unique IDs
        4. load all node files first
        5. then load all relationship files

        For any other user interactions, use the finished tool to defer back to a parent.
    """,
        "tools": [
            neo4j_is_ready, 
            reset_neo4j_data,
            get_physical_schema, 
            read_neo4j_cypher,
            write_neo4j_cypher,
            create_uniqueness_constraint,
            merge_node_into_graph,
            finished
        ]
    }
}