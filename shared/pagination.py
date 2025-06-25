from fastapi import Request
from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = 1
    limit: int = 10
    user_query: str | None = None


async def get_pagination(request: Request):
    page_str = request.query_params.get("page", "1")
    page = int(page_str)

    limit_str = request.query_params.get("limit", "10")
    limit = int(limit_str)

    user_query = request.query_params.get("q", None)

    return Pagination(page=page, limit=limit, user_query=user_query)
