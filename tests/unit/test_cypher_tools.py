"""Unit tests for cypher_tools module."""

import inspect
import pytest

from agentic_kg.tools.cypher_tools import get_neo4j_import_dir


def test_get_neo4j_import_dir_query_contains_correct_filter():
    """Test that get_neo4j_import_dir function uses the correct filter for configuration names.
    
    This test ensures the function searches for 'directories.import' which matches both:
    - server.directories.import (traditional configuration)
    - dbms.directories.import (Community Edition configuration)
    """
    # Get the source code of the function
    source = inspect.getsource(get_neo4j_import_dir)
    
    # Verify the query contains the correct filter
    assert "WHERE name CONTAINS 'directories.import'" in source, (
        "Function should filter for 'directories.import' to match both "
        "'server.directories.import' and 'dbms.directories.import'"
    )
    
    # Verify it doesn't contain the old, more restrictive filter
    assert "WHERE name CONTAINS 'server.directories.import'" not in source, (
        "Function should not use the restrictive 'server.directories.import' filter"
    )


def test_get_neo4j_import_dir_function_signature():
    """Test that the function signature hasn't changed."""
    # Verify the function exists and has the expected signature
    assert callable(get_neo4j_import_dir)
    
    # Check that it takes no parameters
    sig = inspect.signature(get_neo4j_import_dir)
    assert len(sig.parameters) == 0, "Function should take no parameters"