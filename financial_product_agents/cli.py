from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from agents.orchestrator import FinancialProductOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="금융상품 Agent 프로토타입")
    parser.add_argument("query", help="자연어 금융상품 질의")
    parser.add_argument("--full-data", action="store_true", help="샘플 대신 전체 CSV 사용")
    parser.add_argument("--json", action="store_true", help="전체 응답을 JSON으로 출력")
    args = parser.parse_args()
    response = FinancialProductOrchestrator(REPO_ROOT, args.full_data).answer(args.query)
    if args.json:
        print(json.dumps(response.to_dict(), ensure_ascii=False, indent=2))
        return
    print(response.answer)
    if response.warnings:
        print("\n주의:")
        for warning in response.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()

