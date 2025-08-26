import logging

from pathlib import Path
import clevercsv
from itertools import islice

from google.adk.tools import ToolContext
from typing import Dict, Any, List

from agentic_kg.common.tool_result import tool_success, tool_error

from .cypher_tools import get_neo4j_import_dir

logger = logging.getLogger(__name__)

ALL_AVAILABLE_FILES = "all_available_files"
SUGGESTED_FILES = "suggested_file_list"
APPROVED_FILES = "approved_file_list"

def list_import_files(tool_context:ToolContext) -> dict:
    f"""Lists files available for knowledge graph construction.
    All files are relative to the import directory.

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a {ALL_AVAILABLE_FILES} key with list of file names.
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    # get the import dir using the helper function
    result = get_neo4j_import_dir()

    if result["status"] == "error":
        return result
    import_dir = Path(result["neo4j_import_dir"])

    # get a list of relative file names, so files must be rooted at the import dir
    file_names = [str(x.relative_to(import_dir)) 
                 for x in import_dir.rglob("*") 
                 if x.is_file()]

    # save the list to state so we can inspect it later
    tool_context.state[ALL_AVAILABLE_FILES] = file_names

    return tool_success(ALL_AVAILABLE_FILES, file_names)


def set_suggested_files(suggest_files:List[str], tool_context:ToolContext) -> Dict[str, Any]:
    """Set the files to be used for data import.
    """
    tool_context.state[SUGGESTED_FILES] = suggest_files
    return tool_success(SUGGESTED_FILES, suggest_files)

def get_suggested_files(tool_context:ToolContext) -> Dict[str, Any]:
    """Get the suggested files to be used for import.

    Returns:
        dict: A dictionary containing success or failure information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'suggested_files' key with list of files.
              If 'error', includes an 'error_message' key.

    """
    if SUGGESTED_FILES not in tool_context.state:
        return tool_error("Suggested files have not been set. Take no action other than to inform user.")
    return tool_success(SUGGESTED_FILES, tool_context.state[SUGGESTED_FILES])

def approve_suggested_files(tool_context:ToolContext) -> Dict[str, Any]:
    f"""Approves the {SUGGESTED_FILES} in state for further processing as {APPROVED_FILES}."""
    
    if SUGGESTED_FILES not in tool_context.state:
        return tool_error("Current files have not been set. Take no action other than to inform user.")

    tool_context.state[APPROVED_FILES] = tool_context.state[SUGGESTED_FILES]


def get_approved_files(tool_context:ToolContext) -> Dict[str, Any]:
    f"""Get the files that have been approved for importing into a knowledge graph."""
    
    if APPROVED_FILES not in tool_context.state:
        return tool_error("Approved files have not been set.")

    return tool_success(APPROVED_FILES, tool_context.state[APPROVED_FILES])

def sample_file(file_path: str, tool_context: ToolContext) -> dict:
    """Samples a file by reading its content as text.
    
    Treats any file as text and reads up to a maximum of 100 lines.
    
    Args:
      file_path: file to sample, relative to the import directory
      tool_context: ToolContext object
      
    Returns:
        dict: A dictionary containing metadata about the content,
              along with a sampling of the file.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'metadata' key with content details.
              If 'error', includes an 'error_message' key.
    """
    import_dir_result = get_neo4j_import_dir() # chain tool call
    if import_dir_result["status"] == "error": return import_dir_result
    import_dir = Path(import_dir_result["neo4j_import_dir"])
    p = import_dir / file_path
    
    if not p.exists():
        return tool_error(f"Path does not exist: {file_path}")
    
    # Set basic metadata
    result = {
        "metadata": {
            "path": file_path,
        },
        "annotations": []
    }
    
    # Set mimetype based on extension
    file_extension = p.suffix.lower()
    if file_extension == '.csv':
        result["metadata"]["mimetype"] = "text/csv"
    elif file_extension == '.md':
        result["metadata"]["mimetype"] = "text/markdown"
    else:
        result["metadata"]["mimetype"] = "text/plain"
    
    try:
        # Treat all files as text
        with open(p, 'r', encoding='utf-8') as file:
            # Read up to 100 lines
            lines = list(islice(file, 100))
            content = ''.join(lines)
            result["content"] = content
    
    except Exception as e:
        return tool_error(f"Error reading or processing file {file_path}: {e}")
    
    return tool_success("sample", result)


def search_csv_file(file_path: str, query: str, tool_context: ToolContext, case_sensitive: bool = False) -> dict:
    """
    Searches a CSV file for rows containing the given query string in any of its fields.

    Args:
      file_path: Path to the CSV file, relative to the Neo4j import directory.
      query: The string to search for.
      tool_context: The ToolContext object.
      case_sensitive: Whether the search should be case-sensitive (default: False).

    Returns:
        dict: A dictionary with 'status' ('success' or 'error').
              If 'success', includes 'search_results' containing 'matching_rows'
              (a list of rows, where each row is a list of strings)
              and 'metadata' (path, mimetype, query, case_sensitive, rows_found).
              If 'error', includes an 'error_message'.
    """
    import_dir_result = get_neo4j_import_dir()
    if import_dir_result["status"] == "error":
        return import_dir_result
    import_dir = Path(import_dir_result["neo4j_import_dir"])
    p = import_dir / file_path

    if not p.exists():
        return tool_error(f"CSV file does not exist: {file_path}")
    if not p.is_file():
        return tool_error(f"Path is not a file: {file_path}")
    if not (p.suffix.lower() == ".csv"):
        # Basic check, could be enhanced with mimetypes for more accuracy
        logger.warning(f"File {file_path} does not have a .csv extension, but attempting to process as CSV.")

    matching_rows = []
    search_query = query if case_sensitive else query.lower()
    header_row = []

    try:
        # Handle empty query - return no results
        if not query:
            with open(p, 'r', newline='', encoding='utf-8') as csvfile:
                try:
                    # Just read enough to get the header
                    dialect = clevercsv.Sniffer().sniff(csvfile.read(2048))
                    csvfile.seek(0)
                    reader = clevercsv.reader(csvfile, dialect)
                except clevercsv.Error:
                    csvfile.seek(0)
                    reader = clevercsv.reader(csvfile)
                header_row = next(reader, [])
                # Empty query returns no matches, but we still read the header
        else:
            with open(p, 'r', newline='', encoding='utf-8') as csvfile:
                try:
                    # Read a chunk to sniff dialect, then rewind
                    dialect = clevercsv.Sniffer().sniff(csvfile.read(2048))
                    csvfile.seek(0)
                    reader = clevercsv.reader(csvfile, dialect)
                except clevercsv.Error:
                    # Fallback if sniffing fails (e.g., empty or very small file, or not CSV)
                    csvfile.seek(0)
                    reader = clevercsv.reader(csvfile) # Use default dialect
                    logger.warning(f"Could not sniff CSV dialect for {file_path}. Using default dialect.")
                
                header_row = next(reader, []) # Store header, or empty list if file is empty
                
                for row in reader:
                    for field in row:
                        field_to_check = str(field) if case_sensitive else str(field).lower()
                        if search_query in field_to_check:
                            matching_rows.append(row)
                            break # Move to next row once a match is found
    except Exception as e:
        return tool_error(f"Error reading or searching CSV file {file_path}: {e}")

    result_data = {
        "metadata": {
            "path": file_path,
            "mimetype": "text/csv",
            "query": query,
            "case_sensitive": case_sensitive,
            "header": header_row,
            "rows_found": len(matching_rows)
        },
        "matching_rows": matching_rows
    }
    return tool_success("search_results", result_data)

SEARCH_RESULTS = "search_results"

def search_file(file_path: str, query: str) -> dict:
    """
    Searches any text file (markdown, csv, txt)for lines containing the given query string.
    Simple grep-like functionality that works with any text file.
    Search is always case insensitive.

    Args:
      file_path: Path to the file, relative to the Neo4j import directory.
      query: The string to search for.
      tool_context: The ToolContext object.

    Returns:
        dict: A dictionary with 'status' ('success' or 'error').
              If 'success', includes 'search_results' containing 'matching_lines'
              (a list of dictionaries with 'line_number' and 'content' keys)
              and basic metadata about the search.
              If 'error', includes an 'error_message'.
    """
    import_dir_result = get_neo4j_import_dir()
    if import_dir_result["status"] == "error":
        return import_dir_result
    import_dir = Path(import_dir_result["neo4j_import_dir"])
    p = import_dir / file_path

    if not p.exists():
        return tool_error(f"File does not exist: {file_path}")
    if not p.is_file():
        return tool_error(f"Path is not a file: {file_path}")

    # Check if file has an acceptable extension
    file_ext = p.suffix.lower()
    supported_extensions = {".csv", ".md", ".txt"}
    if file_ext not in supported_extensions:
        logger.warning(f"File {file_path} has an unsupported extension {file_ext}, but attempting to search anyway.")

    # Handle empty query - return no results
    if not query:
        return tool_success(SEARCH_RESULTS, {
            "metadata": {
                "path": file_path,
                "query": query,
                "lines_found": 0
            },
            "matching_lines": []
        })

    matching_lines = []
    search_query = query.lower()
    
    try:
        with open(p, 'r', encoding='utf-8') as file:
            # Process the file line by line
            for i, line in enumerate(file, 1):
                line_to_check = line.lower()
                if search_query in line_to_check:
                    matching_lines.append({
                        "line_number": i,
                        "content": line.strip()  # Remove trailing newlines
                    })
                        
    except Exception as e:
        return tool_error(f"Error reading or searching file {file_path}: {e}")

    # Prepare basic metadata
    metadata = {
        "path": file_path,
        "query": query,
        "lines_found": len(matching_lines)
    }
    
    result_data = {
        "metadata": metadata,
        "matching_lines": matching_lines
    }
    return tool_success("search_results", result_data)

async def import_markdown_file(source_file: str, label_name: str, tool_context: ToolContext):
    """Reads the content of a markdown file then creates a text node in Neo4j.
    The node will only have two properties:
    - content: the entire content of the markdown file

    Args:
      source_file: path to the markdown file, relative to the import directory
      label_name: the label applied to the created node
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary indicating success or failure.
              Includes a 'status' key ('success' or 'error').
              If 'error', includes an 'error_message' key.
    """
    from agentic_kg.sub_agents.cypher_agent.tools import create_uniqueness_constraint, write_neo4j_cypher
    
    # 1. Ensure that a property constraint has been created for label/source_file
    constraint_result = await create_uniqueness_constraint(label_name, "source_file")
    if constraint_result["status"] == "error":
        return constraint_result
    
    # 2. Read the content of the markdown
    import_dir_result = get_neo4j_import_dir()
    if import_dir_result["status"] == "error":
        return import_dir_result
    
    import_dir = Path(import_dir_result["neo4j_import_dir"])
    file_path = import_dir / source_file
    
    if not file_path.exists():
        return tool_error(f"Markdown file does not exist: {source_file}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as mdfile:
            content = mdfile.read()
    except Exception as e:
        return tool_error(f"Error reading markdown file {source_file}: {e}")
    
    # 3. Create a node for the markdown using a parameterized cypher query
    query = "MERGE (t:$($label_name) {source_file: $source_file}) SET t.content = $content"
    properties = {
        "label_name": label_name,
        "source_file": source_file,
        "content": content
    }
    return await write_neo4j_cypher(query, properties)
    