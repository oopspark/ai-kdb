from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProductSpec:
    key: str
    label: str
    sample_file: str
    full_file: str
    id_field: str
    name_field: str
    fields: dict[str, str]
    numeric_fields: frozenset[str]
    warnings: tuple[str, ...]


SPECS = {
    "domestic_bond": ProductSpec(
        key="domestic_bond",
        label="국내채권",
        sample_file="국내채권_샘플.csv",
        full_file="국내채권_데이터.csv",
        id_field="PD_NO",
        name_field="PD_NM",
        fields={
            "name": "PD_NM", "category": "STD_PD_MCLS_NM", "bond_type": "BD_KND",
            "currency": "CURR_CD", "maturity": "MAT_DT", "coupon_rate": "SRFC_IRT",
            "credit_grade": "CRD_GRD", "risk_grade": "PD_RISK_GCD",
            "buy_yield": "BUY_YIELD", "after_tax_yield": "AFTER_TAX_YIELD",
            "remaining_days": "REMAINING_DAYS", "duration": "DUR", "price": "EVAL_PRICE",
        },
        numeric_fields=frozenset({"coupon_rate", "risk_grade", "buy_yield", "after_tax_yield", "remaining_days", "duration", "price"}),
        warnings=("매수·세후 수익률은 값이 제공된 일부 종목 안에서만 비교할 수 있습니다.",),
    ),
    "domestic_etf": ProductSpec(
        key="domestic_etf",
        label="국내 ETF",
        sample_file="국내ETF_샘플.csv",
        full_file="국내ETF_데이터.csv",
        id_field="pd_itm_no",
        name_field="pd_nm",
        fields={
            "name": "pd_nm", "short_name": "pd_abrv_nm", "manager": "cu_fund_mgmt_co",
            "base_index": "cu_base_index", "fee": "cu_charge_rt", "leverage": "cu_lev_fector",
            "return_1m": "du_er_1m", "return_3m": "du_er_3m", "return_1y": "du_er_1y",
            "return_ytd": "du_er_ytd", "aum": "du_last_aum", "risk_grade": "pd_risk_cd",
            "risk_name": "pd_risk_nm", "pension": "pd_pen_tr_yn", "asset_type": "wu_inv_ast_type",
            "region": "wu_inv_rgn",
        },
        numeric_fields=frozenset({"fee", "leverage", "return_1m", "return_3m", "return_1y", "return_ytd", "aum"}),
        warnings=("기초지수와 총보수는 일부 종목에만 제공되며 결측값을 0으로 해석하지 않습니다.",),
    ),
    "overseas_etf": ProductSpec(
        key="overseas_etf",
        label="해외 ETF",
        sample_file="해외ETF_샘플.csv",
        full_file="해외ETF_데이터.csv",
        id_field="pd_itm_no",
        name_field="pd_nm",
        fields={
            "name": "pd_nm", "ticker": "pd_abrv_nm", "isin": "pd_isin_cd",
            "manager": "cu_fund_mgmt_co", "base_index": "cu_base_index", "fee": "cu_charge_rt",
            "strategy": "cu_strtegy", "replication": "cu_index_repl_mthd", "aum": "du_last_aum",
            "price": "du_clpr", "volume": "du_vol_1d", "asset_type": "wu_inv_ast_type",
            "region": "wu_inv_rgn", "currency": "pd_trd_ccy",
        },
        numeric_fields=frozenset({"fee", "aum", "price", "volume"}),
        warnings=("1일 수익률 값은 실질 비교에 사용하지 않습니다.", "기초지수의 미제공 안내 문구는 실제 지수명으로 취급하지 않습니다."),
    ),
    "public_fund": ProductSpec(
        key="public_fund",
        label="공모펀드",
        sample_file="공모펀드_샘플.csv",
        full_file="공모펀드_데이터.csv",
        id_field="itm_no",
        name_field="itm_nm",
        fields={
            "name": "itm_nm", "short_name": "itm_abrv_nm", "currency": "curr_cd",
            "region": "fd_ivst_rgn_desc", "fund_type": "or_attr_desc", "benchmark": "bmrk_nm",
            "hedged": "hdge_fd_yn", "return_1m": "fd_mm1_ern_r", "return_3m": "fd_mm3_ern_r",
            "return_1y": "fd_yr1_ern_r", "return_3y": "fd_yr3_ern_r", "return_5y": "fd_yr5_ern_r",
            "aum": "fd_nast_suma", "risk_name": "zrin_fd_ivst_risk_grd_nm", "sale_status": "sale_yn",
            "our_sale": "thco_sale_yn",
        },
        numeric_fields=frozenset({"return_1m", "return_3m", "return_1y", "return_3y", "return_5y", "aum"}),
        warnings=("공모펀드 데이터에는 보수 정보가 없어 보수 비교를 제공할 수 없습니다.", "기간별 수익률은 결측이 많아 값이 있는 상품 안에서만 비교합니다."),
    ),
}


def data_path(repo_root: Path, spec: ProductSpec, full_data: bool) -> Path:
    filename = spec.full_file if full_data else spec.sample_file
    return repo_root / "2.금융상품_데이터" / filename

