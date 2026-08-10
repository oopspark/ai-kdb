#!/usr/bin/env python3
"""Build a YAML catalogue of unique values for all finance data columns."""

from __future__ import annotations

import csv
import json
from pathlib import Path


PRODUCTS = ["국내채권", "국내ETF", "해외ETF", "공모펀드"]
VALUE_LIST_LIMIT = 100

PREFIXES = {
    "cu": "Common Update",
    "du": "Daily Update",
    "nru": "Near Real-Time Update",
    "pd": "Product",
    "ru": "Real-Time Update",
    "wu": "Weekly Update",
}

TOKENS = {
    "abrv": "Abbreviated", "after": "After", "amt": "Amount", "annual": "Annual",
    "applied": "Applied", "ast": "Asset", "attr": "Attribute",
    "avg": "Average", "bal": "Balance", "base": "Base",
    "bd": "Bond", "bmrk": "Benchmark", "bpr": "Base Price",
    "buy": "Purchase", "buyable": "Purchasable", "ccd": "Classification Code",
    "ccy": "Currency", "cd": "Code",
    "charge": "Fee", "chas": "Tracking", "circ": "Circulating",
    "clpr": "Closing Price", "cnt": "Count", "cntl": "Control",
    "co": "Company", "corp": "Corporate", "cov": "Convexity",
    "crd": "Credit", "ctry": "Country", "curr": "Currency",
    "cycl": "Cycle", "depo": "Deposit", "desc": "Description",
    "diff": "Difference", "dir": "Direct", "dirty": "Dirty Price", "days": "Days",
    "divd": "Dividend", "dt": "Date", "dur": "Duration",
    "dvid": "Dividend", "eabrv": "English Abbreviated", "eng": "English",
    "equiv": "Equivalent", "er": "Return", "ern": "Return", "errt": "Error Rate",
    "estb": "Establishment", "etn": "ETN", "eval": "Evaluation",
    "evco": "Evaluation Company", "exchdg": "Currency Hedge",
    "exg": "Exchange", "fector": "Factor", "fd": "Fund", "fund": "Fund",
    "frc": "Foreign Currency", "fss": "Financial Supervisory Service",
    "gcd": "Grade Code", "grd": "Grade", "grp": "Group",
    "hdge": "Hedge", "hpr": "High Price", "id": "Identifier",
    "inav": "Intraday NAV", "index": "Index", "info": "Information",
    "int": "Interest", "inv": "Investment",
    "inverse": "Inverse", "irt": "Interest Rate", "isin": "ISIN",
    "isu": "Issue", "itm": "Item", "itt": "Institution",
    "ivst": "Investment", "knd": "Type", "kofia": "KOFIA",
    "ksd": "KSD", "last": "Latest", "lev": "Leverage",
    "lipper": "Lipper", "lpr": "Low Price", "lste": "Delisting",
    "lst": "Listed", "lstg": "Listing", "ma": "Mirae Asset",
    "mat": "Maturity", "match": "Match", "mcls": "Middle Classification", "mgmt": "Management",
    "mkt": "Market", "mm1": "1-Month", "mm3": "3-Month",
    "mm6": "6-Month", "mm18": "18-Month", "mthd": "Method",
    "mtco": "Management Company", "nast": "Net Asset", "nav": "NAV",
    "ndy": "Next-Day", "net": "Net", "nm": "Name", "no": "Number",
    "ofsfd": "Offshore Fund", "opr": "Opening Price", "or": "Operation",
    "ovrs": "Overseas", "pbcm": "Issuer", "pbff": "Public or Private Fund",
    "pcd": "Pattern Code", "pen": "Pension", "pers": "Individual",
    "pd": "Product", "pfiv": "Professional Investor", "pr": "Price",
    "pref": "Preferential", "price": "Price",
    "pretax": "Pre-Tax", "prfd": "Fund-Specific", "prft": "Profit",
    "prvo": "Private", "pshr": "Per Share", "quantity": "Quantity",
    "r": "Rate", "remain": "Remaining", "remaining": "Remaining",
    "repl": "Replication", "rfn": "Reference", "rgn": "Region",
    "risk": "Risk", "rnf": "Change", "rptt": "Representative",
    "rt": "Rate", "sale": "Sale", "scls": "Small Classification",
    "sect": "Sector", "set": "Setup", "short": "Short", "src": "Source",
    "spac": "SPAC", "srfc": "Coupon", "std": "Standard", "stk": "Share",
    "strtegy": "Strategy", "suma": "Total Amount", "tamt": "Total Amount",
    "tax": "Tax", "tcd": "Type Code", "thco": "Our Company",
    "tracking": "Tracking", "tr": "Trading", "trd": "Trading",
    "trusc": "Trustee Company", "type": "Type", "upt": "Update",
    "us": "US", "val": "Trading Value", "vol": "Trading Volume", "volume": "Volume",
    "wk1": "1-Week", "xtn": "External", "yday": "Previous Day",
    "core": "Core", "yield": "Yield", "yn": "Indicator", "yr1": "1-Year",
    "yr2": "2-Year", "yr3": "3-Year", "yr5": "5-Year",
    "ytd": "Year-to-Date", "zrin": "Zeroin",
    "1d": "1-Day", "5d": "5-Day", "1m": "1-Month",
    "3m": "3-Month", "6m": "6-Month", "1y": "1-Year",
}

FULL_NAME_OVERRIDES = {
    "PD_NO": "Product Number",
    "PD_PBCM": "Product Issuer",
    "ISU_BAL_AMT": "Issue Balance Amount",
    "SRFC_IRT": "Coupon Interest Rate",
    "PD_STD_INFO_UPDATE": "Product Standard Information Update Date",
    "DEPO_EQUIV_YIELD_154": "Deposit-Equivalent Yield at 15.4% Tax Rate",
    "DIRTY": "Dirty Price",
    "NDY_DIRTY": "Next-Day Dirty Price",
    "cu_charge_etc_rt": "Common Update Other Expense Rate",
    "cu_fund_mgmt_co": "Common Update Fund Management Company",
    "cu_upt_dt": "Common Information Update Date",
    "du_upt_dt": "Daily Information Update Date",
    "wu_upt_dt": "Weekly Information Update Date",
    "du_nav_rnf_amt": "Daily Update NAV Change Amount",
    "pd_itm_no_ma": "Mirae Asset Product Number",
    "pd_net_tamt": "Product Net Asset Total Amount",
    "pd_net_rt_ast_pshr": "Product Net Asset Ratio Per Share",
    "fd_set_pcd": "Fund Setup Pattern Code",
    "int_dvd_desc": "Interest and Dividend Classification Description",
    "or_attr_desc": "Operation Attribute Description",
    "or_co_xtn_itt_cd": "Management Company External Institution Code",
    "pfiv_sale_cntl_tcd": "Professional Investor Sale Control Type Code",
    "prvo_pbff_desc": "Private or Public Fund Classification Description",
    "zrin_fd_ivst_risk_gcd": "Zeroin Fund Investment Risk Grade Code",
    "zrin_fd_ivst_risk_grd_nm": "Zeroin Fund Investment Risk Grade Name",
}


def yaml_string(value: str) -> str:
    """JSON strings are valid YAML double-quoted scalar strings."""
    return json.dumps(value, ensure_ascii=False)


def english_full_name(column: str) -> str:
    if column in FULL_NAME_OVERRIDES:
        return FULL_NAME_OVERRIDES[column]
    tokens = column.lower().split("_")
    expanded: list[str] = []
    if tokens and tokens[0] in PREFIXES:
        expanded.append(PREFIXES[tokens.pop(0)])
    for token in tokens:
        expanded.append(TOKENS.get(token, token.upper()))
    return " ".join(expanded)


def load_schema_metadata(schema_path: Path) -> dict[str, dict[str, str]]:
    with schema_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream))
    if len(rows) < 2:
        raise ValueError(f"Invalid schema: {schema_path}")
    header = rows[1]
    positions = {name: index for index, name in enumerate(header)}
    required = {"컬럼명", "컬럼한글명"}
    if not required.issubset(positions):
        raise ValueError(f"Missing schema fields in {schema_path}")
    metadata = {}
    for row in rows[2:]:
        column = row[positions["컬럼명"]]
        metadata[column] = {
            "korean_name": row[positions["컬럼한글명"]],
        }
    return metadata


def sorted_values(values: set[str]) -> list[str]:
    return sorted(values, key=lambda value: (value.casefold(), value))


def append_product(
    output,
    product: str,
    data_path: Path,
    metadata: dict[str, dict[str, str]],
) -> tuple[int, int, int]:
    with data_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        unique_values = {column: set() for column in columns}
        null_counts = {column: 0 for column in columns}
        row_count = 0
        for row_count, row in enumerate(reader, start=1):
            for column, values in unique_values.items():
                value = (row.get(column) or "").strip()
                values.add(value)
                if value == "":
                    null_counts[column] += 1

    output.write(f"{yaml_string(product)}:\n")
    for column in columns:
        if column not in metadata:
            raise ValueError(f"No schema metadata for {product}.{column}")
        values = unique_values[column]
        output.write(f"  {yaml_string(column)}:\n")
        output.write(
            f"    english_full_name: {yaml_string(english_full_name(column))}\n"
        )
        output.write(
            f"    korean_name: {yaml_string(metadata[column]['korean_name'])}\n"
        )
        output.write(f"    count: {len(values)}\n")
        output.write(f"    null_count: {null_counts[column]}\n")
        if len(values) <= VALUE_LIST_LIMIT:
            output.write("    values:\n")
            for value in sorted_values(values):
                if value == "":
                    output.write("      - null\n")
                else:
                    output.write(f"      - {yaml_string(value)}\n")

    unique_count = sum(len(values) for values in unique_values.values())
    listed_columns = sum(
        len(values) <= VALUE_LIST_LIMIT for values in unique_values.values()
    )
    return row_count, unique_count, listed_columns


def main() -> None:
    root = Path.cwd()
    matches = [
        path.parent
        for path in root.rglob("국내채권_데이터.csv")
        if "0_원본파일" not in path.parts
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one processed data directory: {matches}")
    data_dir = matches[0]
    destination = data_dir / "금융상품_컬럼별_고유값.yaml"

    with destination.open("w", encoding="utf-8", newline="\n") as output:
        output.write("# 금융상품 데이터 컬럼별 고유값\n")
        output.write("# 모든 컬럼에 고유값 수(count)를 표시\n")
        output.write("# 고유값이 100개 이하인 컬럼만 values를 표시\n")
        output.write("# 빈 문자열은 null로 표시\n")
        for product in PRODUCTS:
            data_path = data_dir / f"{product}_데이터.csv"
            schema_path = data_dir / f"{product}_스키마.csv"
            metadata = load_schema_metadata(schema_path)
            rows, unique_count, listed_columns = append_product(
                output, product, data_path, metadata
            )
            print(
                f"{product}: rows={rows:,}, unique_values={unique_count:,}, "
                f"columns_with_values={listed_columns}"
            )

    print(f"output={destination}")


if __name__ == "__main__":
    main()
