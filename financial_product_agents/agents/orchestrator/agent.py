from __future__ import annotations

from pathlib import Path

from agents.domestic_bond import DomesticBondAgent
from agents.domestic_etf import DomesticEtfAgent
from agents.evidence import EvidenceAgent
from agents.overseas_etf import OverseasEtfAgent
from agents.public_fund import PublicFundAgent
from agents.query_interpreter import QueryInterpreterAgent
from shared.catalog import SPECS, data_path
from shared.models import AgentResponse


class FinancialProductOrchestrator:
    AGENT_CLASSES = {
        "domestic_bond": DomesticBondAgent,
        "domestic_etf": DomesticEtfAgent,
        "overseas_etf": OverseasEtfAgent,
        "public_fund": PublicFundAgent,
    }

    def __init__(self, repo_root: Path, full_data: bool = False):
        self.repo_root = repo_root
        self.full_data = full_data
        self.interpreter = QueryInterpreterAgent()
        self.evidence_agent = EvidenceAgent()

    def answer(self, query: str) -> AgentResponse:
        plan = self.interpreter.interpret(query)
        if plan.clarification:
            return AgentResponse(answer=plan.clarification, query_plan=plan, warnings=["추가 조건이 필요합니다."])
        assert plan.product_type is not None
        spec = SPECS[plan.product_type]
        agent = self.AGENT_CLASSES[plan.product_type](data_path(self.repo_root, spec, self.full_data))
        results = agent.search(plan)
        evidence, warnings = self.evidence_agent.build(plan, spec, results)
        answer = self._format_answer(spec.label, plan.sort_by, results)
        return AgentResponse(answer, plan, results, evidence, warnings)

    @staticmethod
    def _format_answer(label, sort_by, results):
        if not results:
            return f"조건에 부합하는 {label} 상품을 찾지 못했습니다. 조건을 완화하거나 다른 기준을 지정해 주세요."
        criterion = f" `{sort_by}` 기준" if sort_by else ""
        lines = [f"{label}{criterion} 조회 결과 {len(results)}건입니다."]
        for index, item in enumerate(results, start=1):
            value = item.attributes.get(sort_by) if sort_by else item.product_id
            lines.append(f"{index}. {item.name} — {sort_by or '상품 ID'}: {value}")
        return "\n".join(lines)

