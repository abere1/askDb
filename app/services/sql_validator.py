
import sqlglot
from sqlglot import exp


def validate_sql(sql: str) -> str:
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except sqlglot.errors.ParseError as exc:
        raise ValueError("Invalid SQL syntax") from exc

    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Exactly one SQL query is allowed")

    query = statements[0]

    if not isinstance(query, exp.Select):
        raise ValueError("Only SELECT queries are allowed")

    forbidden = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Create,
        exp.Drop,
        exp.Alter,
        exp.Command,
        exp.Into,
        exp.Lock,
    )

    for node in query.walk():
        if isinstance(node, forbidden):
            raise ValueError("This query contains a prohibited operation")

    return sql
