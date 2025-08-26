from pydantic import AnyUrl, BaseModel, field_validator, computed_field

class Neo4jDsn(AnyUrl):
    allowed_schemes = {
        'neo4j',
        'neo4j+s', 
        'neo4j+ssc', 
        'bolt', 
        'bolt+s', 
        'bolt+ssc'
    }
    user_required = False # assume "neo4j" if not provided


class Neo4jConfig(BaseModel):
    dsn: Neo4jDsn
    
    # validators
    @field_validator('dsn')
    @classmethod
    def validate_dsn(cls, v: Neo4jDsn) -> Neo4jDsn:
        """Ensure DSN includes both a scheme and a host."""
        if not getattr(v, 'scheme', None) or not getattr(v, 'host', None):
            raise ValueError('DSN must include both a scheme and a host')
        # Enforce allowed schemes explicitly to guard against AnyUrl accepting others
        allowed = getattr(Neo4jDsn, 'allowed_schemes', None)
        if allowed and v.scheme not in allowed:
            raise ValueError(f"Invalid scheme '{v.scheme}'. Allowed: {sorted(allowed)}")
        return v

    # computed fields (defaulted/derived accessors)
    @computed_field
    @property
    def scheme(self) -> str:
        return self.dsn.scheme

    @computed_field
    @property
    def host(self) -> str:
        return self.dsn.host

    @computed_field
    @property
    def port(self) -> int:
        return self.dsn.port or 7687

    @computed_field
    @property
    def username(self) -> str:
        return self.dsn.username or "neo4j"

    @computed_field
    @property
    def password(self) -> str | None:
        return self.dsn.password

    @computed_field
    @property
    def database(self) -> str:
        path = (self.dsn.path or '').lstrip('/')
        path_db = path.split('/', 1)[0] if path else None
        return path_db or "neo4j"

    @computed_field
    @property
    def uri(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"

    @computed_field
    @property
    def auth(self) -> tuple[str, str | None]:
        return (self.username, self.password)

    def to_driver_params(self) -> dict:
        """
        Convert the parsed DSN into the common params used to initialize a Neo4j driver.
        Note: This does NOT create a driver or require a live connection.
        """
        # Use computed accessors to centralize defaults/derivations
        return {"uri": self.uri, "auth": self.auth}
    