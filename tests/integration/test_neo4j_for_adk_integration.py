import os
import pytest

pytestmark = pytest.mark.integration

# Skip module if Docker isn't available
try:
    import docker  # type: ignore
    _client = docker.from_env()
    _client.ping()
except Exception as e:  # pragma: no cover
    pytest.skip(f"Docker not available/running: {e}", allow_module_level=True)


def _compose_dsn(bolt_url: str, auth: tuple[str, str | None], database: str = "neo4j") -> str:
    """Build a DSN from bolt URL and auth tuple suitable for Neo4jConfig."""
    # bolt_url expected like bolt://host:port
    username, password = auth
    # username may be None; default to neo4j to align with Neo4jConfig defaults
    userinfo = username or "neo4j"
    if password is not None:
        userinfo = f"{userinfo}:{password}"
    return bolt_url.replace("bolt://", f"bolt://{userinfo}@") + f"/{database}"


def test_neo4j_for_adk_roundtrip_with_testcontainers():
    try:
        from testcontainers.neo4j import Neo4jContainer
    except Exception as e:  # pragma: no cover
        pytest.skip(f"testcontainers not available: {e}")

    from agentic_kg.common.neo4j_for_adk import Neo4jForADK
    from agentic_kg.common.pydantic_neo4j import Neo4jConfig
    
    # Start ephemeral Neo4j
    with Neo4jContainer(image="neo4j:5") as neo4j:
        # Connection info
        try:
            bolt_url = neo4j.get_connection_url()  # e.g., bolt://localhost:7687
        except AttributeError:
            host = "localhost"
            try:
                port = neo4j.get_exposed_port(7687)
            except Exception:
                port = 7687
            bolt_url = f"bolt://{host}:{port}"

        try:
            auth = neo4j.get_auth()  # (username, password)
        except AttributeError:
            auth = ("neo4j", os.getenv("NEO4J_PASSWORD", None))

        dsn = _compose_dsn(bolt_url, auth, database="neo4j")
        cfg = Neo4jConfig(dsn=dsn)

        client = Neo4jForADK(cfg)
        try:
            # Simple read query to validate roundtrip and ADK result envelope
            result = client.send_query("RETURN 1 AS ok")
            assert result["status"] == "success"
            rows = result["result"]
            assert isinstance(rows, list)
            assert len(rows) == 1
            assert rows[0] == {"ok": 1}
        finally:
            client.close()
