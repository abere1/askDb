from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.engine import get_engine


def execute_query(sql: str) -> dict:
    engine = get_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("SET TRANSACTION READ ONLY"))
                connection.execute(
                    text("SET LOCAL statement_timeout = '5000ms'")
                )

                result = connection.execute(text(sql))

                return {
                    "columns": list(result.keys()),
                    "rows": [dict(row) for row in result.mappings().fetchmany(100)],
                }

    except SQLAlchemyError as exc:
        raise RuntimeError("Database query execution failed") from exc

    finally:
        engine.dispose()
