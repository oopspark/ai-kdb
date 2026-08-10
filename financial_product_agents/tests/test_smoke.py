from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from agents.orchestrator import FinancialProductOrchestrator
from agents.query_interpreter import QueryInterpreterAgent


class AgentSmokeTest(unittest.TestCase):
    def setUp(self):
        self.app = FinancialProductOrchestrator(REPO_ROOT)

    def test_overseas_etf_fee_query(self):
        response = self.app.answer("총보수가 낮은 해외 ETF 3개")
        self.assertEqual(response.query_plan.product_type, "overseas_etf")
        self.assertEqual(response.query_plan.sort_by, "fee")
        self.assertEqual(response.query_plan.sort_order, "asc")
        self.assertLessEqual(len(response.results), 3)
        self.assertTrue(response.evidence)

    def test_public_fund_fee_requires_alternative(self):
        response = self.app.answer("보수가 낮은 공모펀드 3개")
        self.assertIn("보수 정보가 없습니다", response.answer)
        self.assertFalse(response.results)

    def test_missing_product_type_requests_clarification(self):
        plan = QueryInterpreterAgent().interpret("수익률이 높은 상품 5개")
        self.assertIsNotNone(plan.clarification)

    def test_domestic_bond_evidence(self):
        response = self.app.answer("매수수익률이 높은 국내채권 2개")
        self.assertEqual(response.query_plan.sort_by, "buy_yield")
        self.assertTrue(any("일부 종목" in warning for warning in response.warnings))

    def test_all_product_agents_are_routable(self):
        queries = {
            "domestic_bond": "표면금리가 높은 국내채권 1개",
            "domestic_etf": "AUM이 높은 국내 ETF 1개",
            "overseas_etf": "총보수가 낮은 해외 ETF 1개",
            "public_fund": "1년 수익률이 높은 공모펀드 1개",
        }
        for expected_type, query in queries.items():
            with self.subTest(product_type=expected_type):
                response = self.app.answer(query)
                self.assertEqual(response.query_plan.product_type, expected_type)
                self.assertTrue(response.results)


if __name__ == "__main__":
    unittest.main()
