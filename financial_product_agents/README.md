# 금융상품 Agent 모듈

참고 문서의 원칙에 따라 **LLM이 수치를 계산하지 않고 CSV 조회 엔진이 검색·정렬한 결과만 설명**하도록 구성한 프로토타입이다.

## 구성

```text
agents/
├── query_interpreter/  # 자연어를 안전한 QueryPlan으로 변환
├── domestic_bond/      # 국내채권 전용 조회
├── domestic_etf/       # 국내 ETF 전용 조회
├── overseas_etf/       # 해외 ETF 전용 조회
├── public_fund/        # 공모펀드 전용 조회
├── evidence/           # 결과·근거·경고 검증
└── orchestrator/       # 위 Agent들의 실행 순서 제어
shared/                 # 공통 계약과 CSV 엔진
```

현재 버전은 외부 패키지 없이 샘플 CSV로 바로 실행된다. 질의 해석기는 결정론적 기본 구현이며, 운영 시 같은 `QueryPlan` 계약을 반환하는 HyperCLOVA X 어댑터로 교체한다. 다른 생성형 LLM 연결은 의도적으로 포함하지 않았다.

## 실행

저장소 루트에서:

```bash
python3 financial_product_agents/cli.py "총보수가 낮은 해외 ETF 3개"
python3 financial_product_agents/cli.py "AUM이 높은 국내 ETF 5개"
python3 -m unittest discover -s financial_product_agents/tests -v
```

기본 데이터 경로는 `2.금융상품_데이터/*_샘플.csv`다. 전체 데이터로 실행하려면 `--full-data`를 추가한다.

```bash
python3 financial_product_agents/cli.py --full-data "AUM이 높은 미국 해외 ETF 5개"
```

## 안전 원칙

- 허용 목록에 등록된 컬럼과 연산자만 조회한다.
- CSV의 결측값은 0으로 바꾸지 않는다.
- 상품군별 데이터 한계를 경고로 반환한다.
- 답변 근거에 원본 행 번호, 상품 ID, 컬럼, 데이터 기준일을 포함한다.
- 공모펀드 보수처럼 제공되지 않은 정보는 명시적으로 답변 불가 처리한다.
- 결과는 투자 추천이 아니라 조건에 부합하는 데이터 조회 결과다.

## 다음 연결 지점

`agents/query_interpreter/agent.py`의 `QueryInterpreterAgent.interpret()` 앞단에 HyperCLOVA X 호출을 연결하고, 응답 JSON을 `QueryPlan.from_dict()`로 검증하면 된다. 모델에게 SQL을 직접 생성·실행시키지 말고 허용된 필터 계약만 생성하게 한다.
