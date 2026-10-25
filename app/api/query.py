
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.sql_generator import generate_sql
from app.services.sql_validator import validate_sql
from app.db.query_executor import execute_query

router = APIRouter(prefix="/query", tags=["Query"])


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)


@router.post("/ask")
def ask_database(request: QuestionRequest):
    try:
        sql = generate_sql(request.question)
        sql = validate_sql(sql)
        result = execute_query(sql)

        return {
            "question": request.question,
            "sql": sql,
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": len(result["rows"]),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        logging.exception("AskDB query failed")
        raise HTTPException(
            status_code=500,
            detail="Could not answer the question. Please try again.",
        )
