#!/usr/bin/env python3
"""Create a compact profile of the four finance CSV datasets."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


SELECTED = {
    "국내채권": [
        "BD_KND", "STD_PD_MCLS_NM", "STD_PD_SCLS_NM", "PD_EVCO_CRD_GRD",
        "PD_RISK_GCD", "CURR_CD", "BUY_YIELD", "AFTER_TAX_YIELD",
        "REMAINING_DAYS", "DUR", "EVAL_PRICE",
    ],
    "국내ETF": [
        "cu_base_index", "cu_charge_rt", "cu_fund_mgmt_co", "cu_lev_fector",
        "du_er_1d", "du_er_1m", "du_er_1y", "du_er_ytd", "du_last_aum",
        "pd_pen_risk_nm", "pd_pen_tr_yn", "pd_risk_nm", "pd_sale_yn",
        "pd_sect_nm", "wu_core_yn", "wu_inv_ast_type", "wu_inv_rgn",
    ],
    "해외ETF": [
        "cu_base_index", "cu_charge_rt", "cu_fund_mgmt_co",
        "cu_index_repl_mthd", "cu_index_tracking_yn", "cu_lev_fector",
        "du_er_1d", "du_last_aum", "pd_exg_mkt_cd", "pd_trd_ccy",
        "pd_sale_yn", "wu_core_yn", "wu_inv_ast_type", "wu_inv_rgn",
    ],
    "공모펀드": [
        "curr_cd", "exchdg_yn", "fd_ivst_rgn_desc", "fd_nast_suma",
        "fd_wk1_ern_r", "fd_mm1_ern_r", "fd_yr1_ern_r", "fd_yr3_ern_r",
        "fd_yr5_ern_r", "or_attr_desc", "ovrs_fd_desc", "pers_corp_desc",
        "prvo_pbff_desc", "sale_yn", "thco_sale_yn",
        "zrin_fd_ivst_risk_grd_nm",
    ],
}


def numeric_summary(values: list[str]) -> dict[str, float | int] | None:
    numbers: list[float] = []
    for value in values:
        try:
            numbers.append(float(value))
        except ValueError:
            return None
    if not numbers:
        return None
    numbers.sort()
    count = len(numbers)
    return {
        "count": count,
        "min": numbers[0],
        "median": numbers[count // 2],
        "max": numbers[-1],
    }


def profile(path: Path, product: str) -> dict:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        nonempty = Counter()
        selected_values = {name: [] for name in SELECTED[product] if name in headers}
        selected_counts = {name: Counter() for name in selected_values}
        rows = 0
        for row in reader:
            rows += 1
            for name in headers:
                value = (row.get(name) or "").strip()
                if value:
                    nonempty[name] += 1
            for name in selected_values:
                value = (row.get(name) or "").strip()
                if value:
                    selected_counts[name][value] += 1
                    if len(selected_values[name]) < 100_000:
                        selected_values[name].append(value)

    fill_rates = {
        name: round(nonempty[name] / rows * 100, 2) if rows else 0
        for name in headers
    }
    lowest = sorted(fill_rates.items(), key=lambda item: (item[1], item[0]))[:12]
    selected = {}
    for name, values in selected_values.items():
        numeric = numeric_summary(values)
        if numeric:
            selected[name] = {
                "fill_rate": fill_rates[name],
                "numeric": numeric,
            }
        else:
            selected[name] = {
                "fill_rate": fill_rates[name],
                "top_values": selected_counts[name].most_common(8),
                "distinct": len(selected_counts[name]),
            }
    return {
        "file": path.name,
        "rows": rows,
        "columns": len(headers),
        "lowest_fill_rates": lowest,
        "selected_columns": selected,
    }


def main() -> None:
    matches = [
        path.parent
        for path in Path.cwd().rglob("국내채권_데이터.csv")
        if "0_원본파일" not in path.parts
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one processed data directory, found {matches}")
    data_dir = matches[0]
    result = {}
    for product in SELECTED:
        result[product] = profile(data_dir / f"{product}_데이터.csv", product)
    output = Path("tmp/finance_profile.json")
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(output)


if __name__ == "__main__":
    main()
