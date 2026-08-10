from __future__ import annotations

import re

from shared.models import Filter, QueryPlan


class QueryInterpreterAgent:
    PRODUCT_WORDS = {
        "국내채권": "domestic_bond", "채권": "domestic_bond",
        "국내 etf": "domestic_etf", "국내etf": "domestic_etf",
        "해외 etf": "overseas_etf", "해외etf": "overseas_etf",
        "공모펀드": "public_fund", "펀드": "public_fund",
    }

    SORT_WORDS = {
        "보수": "fee", "총보수": "fee", "aum": "aum", "순자산": "aum",
        "1개월 수익률": "return_1m", "3개월 수익률": "return_3m",
        "1년 수익률": "return_1y", "3년 수익률": "return_3y", "5년 수익률": "return_5y",
        "세후수익률": "after_tax_yield", "매수수익률": "buy_yield", "표면금리": "coupon_rate",
    }

    def interpret(self, query: str) -> QueryPlan:
        normalized = " ".join(query.lower().split())
        product_type = next((value for word, value in self.PRODUCT_WORDS.items() if word in normalized), None)
        limit_match = re.search(r"(\d+)\s*(?:개|종|건)", normalized)
        limit = min(int(limit_match.group(1)), 20) if limit_match else 5

        if not product_type:
            return QueryPlan(None, limit=limit, clarification="국내채권, 국내 ETF, 해외 ETF, 공모펀드 중 상품군을 지정해 주세요.", original_query=query)

        if product_type == "public_fund" and "보수" in normalized:
            return QueryPlan(product_type, clarification="제공된 공모펀드 데이터에는 보수 정보가 없습니다. 다른 비교 기준을 선택해 주세요.", original_query=query)

        sort_by = next((field for word, field in self.SORT_WORDS.items() if word in normalized), None)
        ascending_words = ("낮은", "낮게", "저렴", "적은", "짧은")
        sort_order = "asc" if any(word in normalized for word in ascending_words) else "desc"
        filters: list[Filter] = []

        region_map = {"미국": "미국" if product_type != "overseas_etf" else "United States", "국내": "국내", "글로벌": "Global"}
        for word, value in region_map.items():
            if word in normalized and not (word == "국내" and product_type in {"domestic_bond", "domestic_etf"}):
                filters.append(Filter("region", "contains", value))
                break

        asset_map = {"주식": "주식" if product_type != "overseas_etf" else "Equity", "채권형": "채권", "원자재": "원자재"}
        for word, value in asset_map.items():
            if word in normalized:
                target = "fund_type" if product_type == "public_fund" else "asset_type"
                filters.append(Filter(target, "contains", value))
                break

        return QueryPlan(product_type, filters, sort_by, sort_order, limit, original_query=query)

