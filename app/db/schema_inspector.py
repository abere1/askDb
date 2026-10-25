
from sqlalchemy import Engine, inspect

def get_database_schema(engine: Engine) -> list[dict]:
    inspector = inspect(engine)
    tables = []

    for schema in inspector.get_schema_names():
        if schema.startswith("pg_") or schema == "information_schema":
            continue

        table_names = inspector.get_table_names(schema=schema)
        view_names = inspector.get_view_names(schema=schema)

        for name, object_type in (
            [(name, "table") for name in table_names]
            + [(name, "view") for name in view_names]
        ):
            columns = inspector.get_columns(name, schema=schema)

            tables.append({
                "schema": schema,
                "name": name,
                "type": object_type,
                "columns": [
                    {
                        "name": column["name"],
                        "data_type": str(column["type"]),
                        "nullable": column["nullable"],
                    }
                    for column in columns
                ],
            })

    return tables