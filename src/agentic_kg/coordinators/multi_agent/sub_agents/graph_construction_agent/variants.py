
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the root agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""

from agentic_kg.tools.user_goal_tools import (
    get_user_goal,  get_approved_user_goal, 
)
from agentic_kg.tools.construction_plan_tools import (
    get_approved_construction_plan, 
)
from agentic_kg.tools.cypher_tools import (
    read_neo4j_cypher, write_neo4j_cypher, create_uniqueness_constraint, 
    get_physical_schema,
)
from agentic_kg.tools.file_tools import get_approved_files
from agentic_kg.tools.kg_construction_tools import build_graph_from_construction_rules
from agentic_kg.tools.adk_tools import finished

variants = {
    "graph_construction_agent_v1": {
        "instruction": """
        You are an expert at knowledge graph construction. Construct a graph using
        the available tools, according to the approved schema and construction rules.

        Before beginning construction, make sure you know the user goal, 
        approved files, approved schema and construction rules.
        - Use the get_approved_user_goal to check the user goal
        - Use the get_approved_files to check the approved files
        - Use the get_approved_construction_plan to check the approved construction rules

        Follow these steps to construct a knowledge graph:
        1. check that the construction rules are valid by comparing the construction plan with the approved files and schema
        2. create appropriate constraints for every node construction using the 'create_uniqueness_constraint' tool
        3. use the 'build_graph_from_construction_rules' tool to build the graph
        4. verify that the graph has been built by comparing the physical schema with the approved schema using the 'read_neo4j_cypher' tool
        5. verify that the graph is reasonable by proposing a hypothetical question that reflects the user goal. try to answer it using the 'read_neo4j_cypher' tool
        6. summarize the state of the graph and your post-construction analysis to the user
        7. invite the user to try some questions that you'll answer using the 'read_neo4j_cypher' tool
        8. when the user is satisfied, use the 'finished' tool to signal that this phase of graph construction is complete

        """,
        "tools": [
            get_approved_user_goal, get_approved_files, get_approved_construction_plan,
            create_uniqueness_constraint, build_graph_from_construction_rules,
            get_physical_schema, read_neo4j_cypher, 
            finished
        ]
    },
}
