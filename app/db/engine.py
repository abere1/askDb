from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine(database_url: str) -> Engine:
    """
    Create a SQLAlchemy engine for the configured database.

    Args:
        database_url: SQLAlchemy-compatible database connection URL.

    Returns:
        A SQLAlchemy Engine.
    """
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    return engine
