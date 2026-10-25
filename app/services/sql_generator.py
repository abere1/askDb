
import json

from groq import Groq

from app.core.config import settings
from app.db.engine import get_engine
from app.db.schema_inspector import get_database_schema


def generate_sql(question: str) -> str:
    engine = get_engine(settings.DATABASE_URL)

    try:
        schema = get_database_schema(engine)
    finally:
        engine.dispose()

    client = Groq(api_key=settings.GROQ_API_KEY)

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a PostgreSQL SQL generator. "
                    "Generate exactly one read-only SELECT query "
                    "that answers the user's question using the "
                    "provided database schema. Use only tables, "
                    "views, and columns present in that schema. "
                    "Do not invent database objects. "
                    "Return only SQL, without Markdown or explanations. "
                    "If the question cannot be answered from the schema, "
                    "do not invent a query. "
                    "Ensure the generated SQL is valid PostgreSQL. "
                    "Never use window functions directly in WHERE or HAVING. "
                    "Calculate window functions in a CTE or subquery, "
                    "then filter their results in an outer query."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Database schema:\n{json.dumps(schema, indent=2)}\n\n"
                    f"User question:\n{question}"
                ),
            },
        ],
    )

    sql = response.choices[0].message.content

    if not sql or not sql.strip():
        raise ValueError("The LLM returned an empty SQL query")

    return sql.strip()
