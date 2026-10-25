# AskDB

AskDB lets you ask questions about a PostgreSQL database in plain English. It inspects the database schema, uses Groq to generate a SQL query, validates the query, and displays the results in a Streamlit interface.

## How it works

1. Enter a question in the Streamlit app or send it to the API.
2. AskDB reads the database schema and sends it with your question to the configured Groq model.
3. The generated query is parsed and restricted to a single `SELECT` statement.
4. The API runs the query in a read-only transaction with a 5-second statement timeout.
5. Results are returned with up to 100 rows and can be downloaded as CSV from the UI.

## Requirements

- Python 3.11 or later
- A PostgreSQL database reachable from the machine or containers running AskDB
- A Groq API key and a model name supported by your Groq account

## Configuration

Create a `.env` file in the project root:

```dotenv
DATABASE_URL=postgresql+psycopg://username:password@hostname:5432/database_name
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_groq_model
```

Use a SQLAlchemy-compatible PostgreSQL URL. Keep `.env` private; it is excluded from the Docker build context and should not be committed.

## Run locally

Create and activate a virtual environment, then install the dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the API in one terminal:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Start the Streamlit UI in another terminal:

```powershell
streamlit run streamlit_app.py
```

Open the UI at <http://localhost:8501>. The API is available at <http://localhost:8000>, and its interactive documentation is at <http://localhost:8000/docs>.

By default, the UI connects to `http://127.0.0.1:8000`. To use a different API address, set `ASKDB_API_URL` in the UI process environment before starting Streamlit.

## Run with Docker Compose

With Docker and the root `.env` file configured, start both services:

```powershell
docker compose up --build
```

Open the UI at <http://localhost:8501> and the API documentation at <http://localhost:8000/docs>. Compose configures the UI to connect to the API container.

If PostgreSQL is running on the host, configure `DATABASE_URL` to use `host.docker.internal` as its hostname so the API container can reach it. For example:

```dotenv
DATABASE_URL=postgresql+psycopg://username:password@host.docker.internal:5432/database_name
```

Stop the services with:

```powershell
docker compose down
```

## API

### `POST /query/ask`

Request:

```json
{
  "question": "How many customers are in each country?"
}
```

The question must contain 1–5000 characters. A successful response includes the original question, generated SQL, result column names, rows, and the number of returned rows:

```json
{
  "question": "How many customers are in each country?",
  "sql": "SELECT ...",
  "columns": ["country", "customer_count"],
  "rows": [{"country": "Canada", "customer_count": 12}],
  "row_count": 1
}
```

Invalid or disallowed SQL returns HTTP 400. Unexpected generation or execution errors return HTTP 500.

## Tests

Run the tests with:

```powershell
pytest
```

The database connection test requires valid `.env` settings and a reachable database containing at least one table or view.
