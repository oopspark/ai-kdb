# 금융상품 에이전트 단계별 구축 실습

`금융상품_에이전트_단계별_구축.ipynb`를 위에서부터 순서대로 실행하면 됩니다.

- 기본 데이터 실습은 외부 API 없이 실행되며, LLM 단계에서는 `openai` SDK를 사용합니다.
- 저장소의 `2.금융상품_데이터/*_샘플.csv`를 읽습니다.
- 질의 해석, 안전한 CSV 검색, 근거 검증, 오케스트레이션을 단계별로 구현합니다.
- `financial_product_ontology.ttl`과 실행용 온톨로지로 동의어·개념 관계·속성 제약을 실습합니다.
- CLOVA Studio API 키 입력, HyperCLOVA X 연결 확인, AI 질의 해석과 근거 기반 답변 생성을 실습합니다.
- API 키는 설정 셀 실행 후 마스킹 입력하며 현재 커널 환경변수에만 보관합니다.
- 마지막에는 `financial_product_agents`의 기존 구현을 호출해 결과를 비교합니다.

노트북은 저장소 루트 또는 이 폴더에서 열어도 경로를 자동으로 찾습니다.

## 터미널에서 HyperCLOVA X와 대화

저장소 루트에서 가상환경을 활성화하고 실행합니다.

```bash
source .venv/bin/activate
python -m pip install openai
python agent_build_practice/clova_chat.py
```

실행 후 CLOVA Studio API 키를 마스킹 입력하면 대화가 시작됩니다. 키는 파일에 저장되지 않습니다.

- `/clear`: 현재 대화 기록 초기화
- `/help`: 명령어 확인
- `/exit`: 종료
