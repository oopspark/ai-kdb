from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Filter:
    field: str
    operator: str
    value: str | float | int


@dataclass
class QueryPlan:
    product_type: str | None
    filters: list[Filter] = field(default_factory=list)
    sort_by: str | None = None
    sort_order: str = "desc"
    limit: int = 5
    clarification: str | None = None
    original_query: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "QueryPlan":
        allowed = {"eq", "contains", "gte", "lte"}
        filters = []
        for item in payload.get("filters", []):
            operator = str(item["operator"])
            if operator not in allowed:
                raise ValueError(f"허용되지 않은 연산자: {operator}")
            filters.append(Filter(str(item["field"]), operator, item["value"]))
        order = str(payload.get("sort_order", "desc"))
        if order not in {"asc", "desc"}:
            raise ValueError(f"허용되지 않은 정렬: {order}")
        return cls(
            product_type=payload.get("product_type"),
            filters=filters,
            sort_by=payload.get("sort_by"),
            sort_order=order,
            limit=max(1, min(int(payload.get("limit", 5)), 20)),
            clarification=payload.get("clarification"),
            original_query=str(payload.get("original_query", "")),
        )


@dataclass
class ProductResult:
    product_type: str
    product_id: str
    name: str
    attributes: dict[str, Any]
    source_file: str
    source_row: int


@dataclass
class AgentResponse:
    answer: str
    query_plan: QueryPlan
    results: list[ProductResult] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data_as_of: str = "2026-07-11"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

