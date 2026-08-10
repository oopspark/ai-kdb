#!/usr/bin/env python3
"""Enrich schema CSVs with Korean names, descriptions, and real examples."""

from __future__ import annotations

import csv
import re
from pathlib import Path


KOREAN_NAMES = {
    # Domestic bonds
    "pd_no": "상품번호",
    "pd_exg_mkt": "상품거래시장",
    "pd_nm": "상품명",
    "pd_abrv_nm": "상품약어명",
    "pd_eng_nm": "상품영문명",
    "pd_abrv_eng_nm": "상품영문약어명",
    "pd_ctry_cd": "상품국가코드",
    "pd_pbcm": "발행기관",
    "std_pd_mcls_nm": "표준상품중분류명",
    "std_pd_scls_nm": "표준상품소분류명",
    "bd_knd": "채권종류",
    "curr_cd": "통화코드",
    "isu_bal_amt": "발행잔액",
    "isu_dt": "발행일자",
    "mat_dt": "만기일자",
    "srfc_irt": "표면금리",
    "pd_evco_crd_grd": "평가회사신용등급",
    "pd_risk_gcd": "상품위험등급코드",
    "pd_std_info_update": "상품기준정보갱신일자",
    "buy_yield": "매수수익률",
    "corp_pretax_yield": "법인세전수익률",
    "corp_after_tax_yield": "법인세후수익률",
    "after_tax_yield": "세후수익률",
    "pref_tax_yield": "우대세율적용수익률",
    "avg_annual_tax_yield": "연평균세후수익률",
    "depo_equiv_yield_154": "예금환산수익률(세율 15.4%)",
    "buyable_quantity": "매수가능수량",
    "remaining_days": "잔존일수",
    "dur": "듀레이션",
    "cov": "컨벡서티",
    "ndy_dur": "익일듀레이션",
    "ndy_cov": "익일컨벡서티",
    "eval_price": "평가가격",
    "applied_yield": "적용수익률",
    "dirty": "경과이자포함가격",
    "ndy_eval_price": "익일평가가격",
    "ndy_applied_yield": "익일적용수익률",
    "ndy_dirty": "익일경과이자포함가격",
    "crd_grd": "신용등급",
    "crd_grd_dt": "신용등급평가일자",

    # Overseas ETFs
    "cu_base_index": "기초지수",
    "cu_charge_rt": "총보수요율",
    "cu_etn_yn": "ETN여부",
    "cu_fund_mgmt_co": "운용사",
    "cu_index_repl_mthd": "지수복제방식",
    "cu_index_tracking_yn": "지수추종여부",
    "cu_inverse_short_yn": "인버스·숏여부",
    "cu_lev_fector": "레버리지배수",
    "cu_strtegy": "운용전략",
    "cu_upt_dt": "기본정보갱신일자",
    "du_base_dt_match_yn": "기준일자일치여부",
    "du_bpr": "기준가",
    "du_clpr": "종가",
    "du_clpr_base_dt": "종가기준일자",
    "du_clpr_src": "종가출처",
    "du_diff_rt": "괴리율",
    "du_er_1d": "1일수익률",
    "du_hpr": "고가",
    "du_last_aum": "최근운용자산규모",
    "du_last_nav": "최근순자산가치",
    "du_lpr": "저가",
    "du_nav_base_dt": "순자산가치기준일자",
    "du_opr": "시가",
    "du_upt_dt": "일간정보갱신일자",
    "du_val_1d": "1일거래대금",
    "du_vol_1d": "1일거래량",
    "pd_curr_cd": "상품통화코드",
    "pd_exg_mkt_cd": "거래소시장코드",
    "pd_grp_no": "상품군번호",
    "pd_isin_cd": "ISIN코드",
    "pd_itm_no": "상품번호",
    "pd_itm_no_ma": "미래에셋상품번호",
    "pd_lipper_id": "리퍼펀드식별자",
    "pd_lstg_dt": "상장일자",
    "pd_lst_price": "상장가격",
    "pd_lst_stk_cnt": "상장주식수",
    "pd_mkt_id": "시장식별자",
    "pd_sale_yn": "상품판매여부",
    "pd_trd_ccy": "거래통화",
    "pd_tr_yn": "상품거래가능여부",
    "pd_us_cik": "미국SEC CIK",
    "ru_mkt_price": "실시간시장가격",
    "ru_mkt_volume": "실시간거래량",
    "wu_core_yn": "핵심ETF여부",
    "wu_inv_ast_type": "투자자산유형",
    "wu_inv_rgn": "투자지역",
    "wu_upt_dt": "주간정보갱신일자",
}


SPECIAL_DESCRIPTIONS = {
    "dur": "채권 원금 회수기간을 현재가치로 가중평균한 값으로, 금리 변화에 대한 가격 민감도를 나타냅니다.",
    "cov": "금리 변화와 채권 가격 변화 간 곡률인 컨벡서티를 나타냅니다.",
    "dirty": "클린가격에 발생한 경과이자를 더한 채권 가격입니다.",
    "ndy_dur": "다음 영업일 기준으로 계산한 채권 듀레이션입니다.",
    "ndy_cov": "다음 영업일 기준으로 계산한 채권 컨벡서티입니다.",
    "ndy_dirty": "다음 영업일 기준 경과이자를 포함한 채권 가격입니다.",
    "cu_base_index": "ETF 또는 ETN이 성과 추종의 기준으로 삼는 기초지수입니다.",
    "cu_index_repl_mthd": "기초지수를 실물·최적화·합성 등의 방식으로 복제하는 방법입니다.",
    "cu_strtegy": "상품이 목표 수익을 추구하기 위해 사용하는 운용 전략입니다.",
    "du_diff_rt": "시장가격과 순자산가치 간 차이를 순자산가치 대비 비율로 나타낸 값입니다.",
    "pd_isin_cd": "국제 표준에 따라 금융상품을 식별하는 ISIN 코드입니다.",
    "pd_us_cik": "미국 증권거래위원회(SEC)가 부여한 중앙색인키(CIK)입니다.",
    "pd_lipper_id": "Lipper 데이터에서 펀드 또는 ETF를 식별하는 고유 값입니다.",
}

NAME_CORRECTIONS = {
    "pd_dvid_cycl": "배당주기",
    "du_lpr": "저가",
}

FALLBACK_EXAMPLES = {
    "pd_dvid_cycl": "분기",
    "pd_sect_nm": "주식",
    "cu_lev_fector": "1.0",
}


def particle(word: str) -> str:
    if not word:
        return "을"
    last = ord(word[-1])
    if 0xAC00 <= last <= 0xD7A3:
        return "을" if (last - 0xAC00) % 28 else "를"
    return "을"


def description(column: str, korean_name: str) -> str:
    key = column.lower()
    if key in SPECIAL_DESCRIPTIONS:
        return SPECIAL_DESCRIPTIONS[key]
    if "여부" in korean_name:
        return f"{korean_name.removesuffix('여부')}에 해당하는지를 Y/N 또는 코드값으로 나타냅니다."
    if korean_name.endswith("일자"):
        return f"{korean_name.removesuffix('일자')}의 기준 날짜를 나타냅니다."
    if korean_name.endswith("코드"):
        return f"{korean_name.removesuffix('코드')}을 식별하거나 분류하기 위한 코드입니다."
    if korean_name.endswith(("번호", "식별자")):
        return f"{korean_name}로 상품이나 대상을 고유하게 식별합니다."
    if any(term in korean_name for term in ("수익률", "요율", "금리", "비율", "오차율")):
        return f"{korean_name}{particle(korean_name)} 비율 또는 백분율 값으로 나타냅니다."
    if any(term in korean_name for term in ("가격", "기준가", "종가", "시가", "고가", "저가")):
        return f"{korean_name}{particle(korean_name)} 해당 통화 단위의 가격 값으로 나타냅니다."
    if any(term in korean_name for term in ("금액", "총액", "잔액", "순자산", "거래대금", "운용자산규모")):
        return f"{korean_name}{particle(korean_name)} 해당 통화 단위의 금액으로 나타냅니다."
    if any(term in korean_name for term in ("수량", "거래량", "주식수", "일수")):
        return f"{korean_name}{particle(korean_name)} 수량 값으로 나타냅니다."
    if korean_name.endswith(("명", "이름")):
        return f"{korean_name.removesuffix('명')}의 공식 명칭입니다."
    if "통화" in korean_name:
        return f"{korean_name}{particle(korean_name)} 나타냅니다."
    return f"{korean_name}{particle(korean_name)} 나타내는 값입니다."


def find_data_file(schema_path: Path) -> Path:
    prefix = schema_path.name.split("_schema__", 1)[0]
    candidates = sorted(schema_path.parent.glob(f"{prefix}_*_datarows.csv"))
    if len(candidates) != 1:
        raise RuntimeError(
            f"{schema_path.name}: expected one datarows CSV, found {len(candidates)}"
        )
    return candidates[0]


def collect_examples(data_path: Path, wanted: set[str]) -> dict[str, str]:
    examples: dict[str, str] = {}
    with data_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        header_lookup = {name.lower(): name for name in reader.fieldnames or []}
        missing = wanted - header_lookup.keys()
        if missing:
            raise RuntimeError(f"{data_path.name}: missing columns {sorted(missing)}")
        for row in reader:
            for key in wanted - examples.keys():
                value = row.get(header_lookup[key], "")
                if value is not None and value.strip():
                    examples[key] = value.strip()
            if len(examples) == len(wanted):
                break
    return examples


def enrich_schema(schema_path: Path) -> tuple[int, int, int]:
    with schema_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream))
    if len(rows) < 2:
        raise RuntimeError(f"{schema_path.name}: invalid schema")

    header = rows[1]
    positions = {name: index for index, name in enumerate(header)}
    required = {"컬럼명", "PK/FK", "컬럼타입", "컬럼한글명", "컬럼값 예시"}
    if not required.issubset(positions):
        raise RuntimeError(f"{schema_path.name}: unsupported schema header")
    schema_rows = rows[2:]
    wanted = {row[0].lower() for row in schema_rows if row}
    examples = collect_examples(find_data_file(schema_path), wanted)
    filled_names = 0
    filled_examples = 0

    output = [rows[0], [
        "컬럼명", "PK/FK", "컬럼타입", "컬럼한글명", "컬럼설명", "컬럼값 예시"
    ]]
    for row in schema_rows:
        def value(name: str) -> str:
            index = positions[name]
            return row[index] if index < len(row) else ""

        column = value("컬럼명")
        key_flag = value("PK/FK")
        data_type = value("컬럼타입")
        korean_name = value("컬럼한글명")
        old_example = value("컬럼값 예시")
        key = column.lower()
        if key in NAME_CORRECTIONS:
            korean_name = NAME_CORRECTIONS[key]
        elif not korean_name.strip():
            korean_name = KOREAN_NAMES.get(key, "")
            if korean_name:
                filled_names += 1
        if not korean_name:
            raise RuntimeError(f"{schema_path.name}: no Korean name for {column}")
        example = examples.get(key, old_example or FALLBACK_EXAMPLES.get(key, ""))
        if example:
            filled_examples += 1
        output.append([
            column, key_flag, data_type, korean_name,
            description(column, korean_name), example,
        ])

    with schema_path.open("w", encoding="utf-8-sig", newline="") as stream:
        csv.writer(stream, lineterminator="\n").writerows(output)
    return len(schema_rows), filled_names, filled_examples


def main() -> None:
    root = Path.cwd()
    schemas = sorted(root.rglob("*_schema__Sheet1_Schema.csv"))
    if not schemas:
        raise SystemExit("No schema CSV files found.")
    for schema in schemas:
        total, names, examples = enrich_schema(schema)
        print(
            f"{schema.name}: {total} columns, "
            f"{names} Korean names filled, {examples} examples populated"
        )


if __name__ == "__main__":
    main()
