from fastapi import FastAPI

from app.api.query import router as query_router

app = FastAPI(title="AskDB")

app.include_router(query_router)