from sqlalchemy import text

from app.core.config import settings
from app.db.engine import get_engine
from app.db.schema_inspector import get_database_schema


def test_database_connection_and_schema_discovery():
    engine = get_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar_one() == 1

        schema = get_database_schema(engine)
        assert isinstance(schema, list)
        assert len(schema) > 0

    finally:
        engine.dispose()