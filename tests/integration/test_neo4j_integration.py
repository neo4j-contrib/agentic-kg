import os
import pytest

# Mark entire module as integration tests
pytestmark = pytest.mark.integration

# Sanity check: ensure Docker daemon is reachable; otherwise skip at module level
try:
    import docker  # type: ignore
    client = docker.from_env()
    client.ping()
except Exception as e:  # pragma: no cover
    pytest.skip(f"Docker not available/running: {e}", allow_module_level=True)


def test_neo4j_container_and_driver_roundtrip():
    try:
        from testcontainers.neo4j import Neo4jContainer
    except Exception as e:  # pragma: no cover - dependency or environment issues
        pytest.skip(f"testcontainers not available: {e}")

    # Start a temporary Neo4j instance
    with Neo4jContainer(image="neo4j:5") as neo4j:
        # Prefer container helpers when available
        try:
            bolt_url = neo4j.get_connection_url()
        except AttributeError:  # older/newer API fallback
            # Best-effort: construct URL from exposed port
            host = "localhost"
            try:
                port = neo4j.get_exposed_port(7687)
            except Exception:
                port = 7687
            bolt_url = f"bolt://{host}:{port}"

        try:
            auth = neo4j.get_auth()  # (username, password)
        except AttributeError:
            # Default fallback; many images use neo4j/<password>
            auth = ("neo4j", os.getenv("NEO4J_PASSWORD", None))

        # Use the official Neo4j Python driver to validate connectivity
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(bolt_url, auth=auth)
        try:
            with driver.session(database="neo4j") as session:
                result = session.run("RETURN 1 AS ok").single()
                assert result["ok"] == 1
        finally:
            driver.close()
