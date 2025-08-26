import pytest
from pydantic import ValidationError

from agentic_kg.common.pydantic_neo4j import Neo4jConfig


def test_neo4j_dsn_with_user_pass_host_port_and_db_in_path():
    cfg = Neo4jConfig(dsn="neo4j://alice:secret@db.local:7687/mydb")

    # Validate pydantic parsed pieces
    assert cfg.dsn.scheme == "neo4j"
    assert cfg.dsn.username == "alice"
    assert cfg.dsn.password == "secret"
    assert cfg.dsn.host == "db.local"
    assert cfg.dsn.port == 7687
    assert cfg.dsn.path == "/mydb"

    # Validate driver parameter mapping
    params = cfg.to_driver_params()
    assert params["uri"] == "neo4j://db.local:7687"
    assert params["auth"] == ("alice", "secret")
    # database is exposed via computed field on the config
    assert cfg.database == "mydb"


def test_bolt_scheme_with_default_port_and_default_database_from_none():
    cfg = Neo4jConfig(dsn="bolt://bob@10.0.0.2")

    # Pydantic parsed pieces
    assert cfg.dsn.scheme == "bolt"
    assert cfg.dsn.username == "bob"
    assert cfg.dsn.password is None
    assert cfg.dsn.host == "10.0.0.2"
    assert cfg.dsn.port is None  # not provided in DSN

    # Mapping uses default port 7687 when not present
    params = cfg.to_driver_params()
    assert params["uri"] == "bolt://10.0.0.2:7687"
    assert params["auth"] == ("bob", None)  # password None when omitted
    # with no path provided, database falls back to default
    assert cfg.database == "neo4j"


def test_missing_user_defaults_username_via_computed_field():
    cfg = Neo4jConfig(dsn="neo4j://localhost:7687")
    # username defaults to "neo4j" when not provided
    assert cfg.username == "neo4j"
    assert cfg.auth == ("neo4j", None)


def test_invalid_scheme_is_rejected():
    with pytest.raises(ValidationError):
        Neo4jConfig(dsn="http://neo4j.local:7687")
