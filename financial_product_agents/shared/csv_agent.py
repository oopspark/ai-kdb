from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .catalog import ProductSpec
from .models import Filter, ProductResult, QueryPlan


EMPTY_VALUES = {"", "null", "none", "nan"}


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return None if text.lower() in EMPTY_VALUES else text


def _number(value: Any) -> float | None:
    text = _clean(value)
    if text is None:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


class CsvProductAgent:
    def __init__(self, spec: ProductSpec, csv_path: Path):
        self.spec = spec
        self.csv_path = csv_path

    def _matches(self, row: dict[str, str], item: Filter) -> bool:
        if item.field not in self.spec.fields:
            raise ValueError(f"{self.spec.label}에서 허용되지 않은 필드: {item.field}")
        raw = row.get(self.spec.fields[item.field])
        if item.operator == "contains":
            return _clean(raw) is not None and str(item.value).casefold() in str(raw).casefold()
        if item.operator == "eq":
            return _clean(raw) is not None and str(raw).strip().casefold() == str(item.value).strip().casefold()
        left = _number(raw)
        right = _number(item.value)
        if left is None or right is None:
            return False
        return left >= right if item.operator == "gte" else left <= right

    def search(self, plan: QueryPlan) -> list[ProductResult]:
        if plan.sort_by and plan.sort_by not in self.spec.fields:
            raise ValueError(f"{self.spec.label}에서 허용되지 않은 정렬 필드: {plan.sort_by}")
        matches: list[tuple[dict[str, str], int]] = []
        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row_number, row in enumerate(csv.DictReader(handle), start=2):
                if all(self._matches(row, item) for item in plan.filters):
                    matches.append((row, row_number))

        if plan.sort_by:
            csv_field = self.spec.fields[plan.sort_by]
            numeric = plan.sort_by in self.spec.numeric_fields
            present = [
                (row, num) for row, num in matches
                if (_number(row.get(csv_field)) is not None if numeric else _clean(row.get(csv_field)) is not None)
            ]
            present.sort(
                key=lambda pair: _number(pair[0].get(csv_field)) if numeric else str(pair[0].get(csv_field)).casefold(),
                reverse=plan.sort_order == "desc",
            )
            matches = present

        results = []
        for row, row_number in matches[: plan.limit]:
            attributes = {name: _clean(row.get(csv_name)) for name, csv_name in self.spec.fields.items()}
            results.append(ProductResult(
                product_type=self.spec.key,
                product_id=_clean(row.get(self.spec.id_field)) or "UNKNOWN",
                name=_clean(row.get(self.spec.name_field)) or "이름 미제공",
                attributes=attributes,
                source_file=str(self.csv_path),
                source_row=row_number,
            ))
        return results
