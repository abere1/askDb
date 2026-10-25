# AskDB — Talk to Your Database. Get Real Answers.

**Ask questions in plain English. Get real data from PostgreSQL. No SQL writing required.**

AskDB is a natural-language database querying application built with FastAPI, PostgreSQL, Groq, and Streamlit. It translates questions into SQL, validates the generated queries, executes them against your own database, and presents the actual results in an interactive interface.

Instead of manually writing complex SQL, users can ask questions about their data and let AskDB handle the query generation and execution.

> AskDB works with different PostgreSQL database schemas through dynamic schema inspection. It does not require a predefined business schema or a bundled database.

---

## The Idea

Working with data often means knowing SQL, understanding a database's schema, and manually writing queries to retrieve useful information.

AskDB simplifies that workflow.

**Ask a question → Generate SQL → Validate the query → Execute against PostgreSQL → Display the results.**

For example, a user might ask:

- Which products have the lowest stock?
- What are the top-performing products by revenue?
- Which customers have placed the most orders?
- Show monthly revenue and compare it with the previous month.
- Rank customers by spending within each country.
- Calculate average order values and identify recent purchasing trends.

The actual questions you can answer depend on the tables, columns, and data in your connected database.

## Features

- **Natural-language querying:** Describe the data you need without writing SQL manually.
- **Dynamic schema inspection:** Discover database tables, views, and columns at runtime.
- **LLM-powered SQL generation:** Use Groq to translate natural-language questions into PostgreSQL queries.
- **SQL validation:** Parse generated SQL and reject disallowed statements before execution.
- **Read-only query execution:** Execute approved queries without intentionally modifying database records.
- **Live database results:** Return actual query results instead of merely suggesting SQL.
- **Interactive interface:** Ask questions and inspect results through Streamlit.
- **SQL transparency:** View the generated SQL to understand how an answer was obtained.
- **CSV export:** Download query results for further analysis.
- **REST API:** Access AskDB through FastAPI.
- **Docker support:** Build and run the application in containers.
- **Bring your own database:** Connect your own PostgreSQL database without bundling its data into the application.

## How It Works

```mermaid
flowchart TD
    A["User asks a question"] --> B["Streamlit Interface"]
    B --> C["FastAPI Endpoint"]
    C --> D["Inspect PostgreSQL Schema"]
    D --> E["Groq SQL Generator"]
    E --> F["SQL Validator"]
    F --> G["PostgreSQL Query Executor"]
    G --> H["Actual Database Results"]
    H --> I["Display Results and SQL"]
```

### 1. Schema inspection

AskDB inspects the connected database to discover the available tables, views, and columns. This information provides context for generating queries against the user's actual schema.

### 2. SQL generation

The schema and natural-language question are sent to the configured Groq model, which generates a PostgreSQL query.

### 3. SQL validation

The generated query passes through a validation layer that parses the SQL and checks for disallowed operations. AskDB is designed to accept a single read-only `SELECT` query rather than arbitrary SQL commands.

### 4. Query execution

Validated SQL is executed against the configured PostgreSQL database. The application returns the result columns and rows to the API.

### 5. Result presentation

The Streamlit interface displays the results, exposes the generated SQL, and provides CSV export functionality.

## Architecture

| Component | Technology | Responsibility |
|---|---|---|
| API | FastAPI | Receives questions and returns results |
| Language model | Groq API | Generates PostgreSQL queries |
| Database connectivity | SQLAlchemy | Connects to PostgreSQL and executes queries |
| SQL parsing | SQLGlot | Parses SQL and supports validation |
| Database | PostgreSQL | Stores the user's actual data |
| Frontend | Streamlit | Provides the interactive query interface |
| Containerization | Docker and Docker Compose | Builds and runs the application services |

## Project Structure

```text
AskDB/
├── app/
│   ├── api/
│   │   └── query.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── engine.py
│   │   ├── schema_inspector.py
│   │   └── query_executor.py
│   ├── services/
│   │   ├── sql_generator.py
│   │   └── sql_validator.py
│   └── main.py
├── tests/
├── streamlit_app.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .gitignore
└── README.md
```

## Getting Started

You can run AskDB locally with Python or run the application using Docker.

### Prerequisites

- Python 3.11 or compatible
- A running PostgreSQL database that you can access
- A Groq API key
- Docker Desktop and Docker Compose for the containerized setup

### Option 1: Run with Docker

**1. Clone the repository**

```bash
git clone https://github.com/biniyamsav/AskDB.git
cd AskDB
```

**2. Configure environment variables**

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@host.docker.internal:5432/YOUR_DATABASE
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-20b
```

Replace the example database credentials and database name with your own values.

For Docker Desktop on Windows, `host.docker.internal` allows a container to reach a database running on the host machine. Your PostgreSQL server must accept that connection.

If PostgreSQL is running on another machine, use its reachable hostname or address instead.

**3. Build and start AskDB**

```bash
docker compose up --build
```

Docker builds the application images and starts the FastAPI and Streamlit services. The PostgreSQL database remains external to Docker.

**4. Open AskDB**

| Service | URL |
|---|---|
| Streamlit interface | http://localhost:8501 |
| FastAPI | http://localhost:8000 |
| Interactive API documentation | http://localhost:8000/docs |

To stop the services, press `Ctrl+C`. To stop the Compose-managed containers separately, run:

```bash
docker compose down
```

### Option 2: Run Locally with Python

**1. Create and activate a virtual environment**

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure `.env`**

Use your own PostgreSQL connection string and Groq API key. When running the API directly on the same machine as PostgreSQL, the database hostname can usually be `localhost`.

**4. Start the API**

```bash
uvicorn app.main:app --reload
```

**5. Start the interface**

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run streamlit_app.py
```

Open http://localhost:8501.

## API Usage

AskDB exposes a natural-language query endpoint.

**Endpoint**

```http
POST /query/ask
```

**Request**

```json
{
  "question": "Show the top five products by total sales"
}
```

**Example response structure**

```json
{
  "question": "Show the top five products by total sales",
  "sql": "SELECT ...",
  "columns": ["product_name", "total_sales"],
  "rows": [
    ["Example Product A", 15000],
    ["Example Product B", 12000]
  ],
  "row_count": 2
}
```

The response above illustrates the structure; the SQL, columns, and rows depend on the connected database and the generated query.

You can also explore the endpoint and send requests through the Swagger UI at http://localhost:8000/docs.

## Security and Limitations

AskDB includes safeguards, but generated SQL should never be treated as automatically correct or completely safe.

- **Read-only validation:** Generated statements are checked before execution. This is an application-level safeguard, not a substitute for database permissions.
- **Database permissions:** Use a dedicated PostgreSQL role with only the required read access. Do not connect using a database superuser in production.
- **Credentials:** Keep `.env` out of Git and never expose API keys in source code, logs, screenshots, or public repositories.
- **Query correctness:** Language models can generate invalid SQL or misunderstand a question. Inspect the generated query when accuracy matters.
- **Query cost:** Complex queries may be slow or expensive. Use appropriate database-side timeouts and resource limits.
- **Schema compatibility:** AskDB discovers schemas dynamically, but query quality depends on the schema and its clarity. It cannot answer questions requiring data that is unavailable in the connected database.
- **Database availability:** The PostgreSQL server must be reachable from the environment where the API is running.

For production use, additional testing, stronger database isolation, authentication, monitoring, and resource controls are recommended.

## Configuration

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy PostgreSQL connection URL |
| `GROQ_API_KEY` | API key used to access Groq |
| `GROQ_MODEL` | Groq model used for SQL generation |
| `ASKDB_API_URL` | Optional Streamlit setting for the FastAPI address; defaults to `http://127.0.0.1:8000` when running locally |

The Docker Compose configuration sets the UI's API address to `http://api:8000`, which resolves to the API service on the Compose network.

## Design Principles

AskDB follows a few core principles:

1. **Bring your own data.** The application does not need a bundled business database.
2. **Discover instead of hardcode.** Database structure is inspected dynamically instead of assuming fixed business tables.
3. **Generate, validate, execute.** The objective is to retrieve real data, not merely produce SQL suggestions.
4. **Keep the query visible.** Users can inspect the SQL behind the returned results.
5. **Separate the application from the database.** Docker packages the application services while users retain control of their PostgreSQL instance.

## Roadmap

Potential future improvements include:

- Automatic correction and retry for recoverable SQL errors
- Better handling of ambiguous questions and missing schema information
- Query-result pagination and configurable result limits
- Query execution metrics and performance monitoring
- Authentication and multi-user support
- More comprehensive automated tests
- Improved query explanations and result summaries
- Support for additional database engines

These are planned improvements, not claims about current functionality.

## Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change.
4. Add or update tests where appropriate.
5. Open a pull request describing the change.

Please never include database credentials, API keys, or private data in a contribution.

## License

No license has been specified yet. Add a `LICENSE` file before presenting AskDB as an open-source project with explicit reuse permissions.

---

**Built by [Biniyam Worku Desta](https://github.com/biniyamsav)**

[GitHub Repository](https://github.com/biniyamsav/AskDB)
