from __future__ import annotations

from pathlib import Path

from shared.catalog import ProductSpec
from shared.models import ProductResult, QueryPlan


class EvidenceAgent:
    def build(self, plan: QueryPlan, spec: ProductSpec, results: list[ProductResult]):
        evidence = []
        for item in results:
            fields = {key: value for key, value in item.attributes.items() if value is not None}
            evidence.append({
                "product_id": item.product_id,
                "product_name": item.name,
                "source_file": Path(item.source_file).name,
                "source_row": item.source_row,
                "used_fields": fields,
            })
        warnings = list(spec.warnings)
        warnings.append("이 결과는 제공 데이터의 조건 조회 결과이며 투자 권유가 아닙니다.")
        if not results:
            warnings.insert(0, "조건에 부합하면서 필요한 값이 존재하는 상품을 찾지 못했습니다.")
        return evidence, warnings

