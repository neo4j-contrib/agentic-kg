
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the cypher agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""

from agentic_kg.tools.user_goal_tools import get_approved_user_goal

from agentic_kg.tools.file_tools import (
    list_import_files, sample_file, search_file,
    set_suggested_files, approve_suggested_files, get_suggested_files
)

from agentic_kg.tools.adk_tools import finished

variants = {    
    "file_suggestion_agent_v1":
        {
            "instruction": """
                You are a constructive critic AI reviewing a list of files. 
                Your primary goal is to suggest files with content that is relevant to a user goal.

                **Task:**
                Review the file list for relevance to the kind of graph and description specified in the approved user goal. 

                For any file that you're not sure about, use the 'sample_file' tool to get 
                a better understanding of the file contents. 

                Only consider structured data files like CSV or JSON.

                Prepare for the task:
                - use the 'get_approved_user_goal' tool to get the approved user goal
                - if the get_approved_user_goal tool returns an error, delegate to another agent using the 'finished' tool

                Think carefully, repeating these steps until finished:
                1. list available files using the 'list_available_files' tool
                2. evaluate the relevance of each file, then record the list of suggested files using the 'set_suggested_files' tool
                3. use the 'get_suggested_files' tool to get the list of suggested files
                4. ask the user to approve the set of suggested files
                5. If the user has feedback, go back to step 1 with that feedback in mind
                6. If approved, use the 'approve_suggested_files' tool to record the approval
                7. When the file approval has been recorded, use the 'finished' tool
                """,
            "tools": [
                get_approved_user_goal, 
                list_import_files, sample_file, search_file,
                set_suggested_files, approve_suggested_files, 
                get_suggested_files,
                finished
            ]
        },
}
