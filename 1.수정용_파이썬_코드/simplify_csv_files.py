#!/usr/bin/env python3
"""Rename finance CSVs and create compact preview samples."""

from __future__ import annotations

import csv
import shutil
from itertools import islice
from pathlib import Path


PRODUCTS = {
    "국내채권": {
        "data": "PRBD01N001_국내채권마스터_20260711_datarows.csv",
        "schema": "PRBD01N001_국내채권마스터_schema__Sheet1_Schema.csv",
    },
    "국내ETF": {
        "data": "PREF01N001_국내ETF마스터_20260711_datarows.csv",
        "schema": "PREF01N001_국내ETF마스터_schema__Sheet1_Schema.csv",
    },
    "해외ETF": {
        "data": "PREF02N001_해외ETF마스터_20260711_datarows.csv",
        "schema": "PREF02N001_해외ETF마스터_schema__Sheet1_Schema.csv",
    },
    "공모펀드": {
        "data": "PRFD01N001_공모펀드마스터_20260711_datarows.csv",
        "schema": "PRFD01N001_공모펀드마스터_schema__Sheet1_Schema.csv",
    },
}


def create_sample(data_path: Path, sample_path: Path, row_limit: int = 100) -> int:
    with data_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        rows = list(islice(reader, row_limit + 1))
    with sample_path.open("w", encoding="utf-8-sig", newline="") as target:
        csv.writer(target, lineterminator="\n").writerows(rows)
    return max(0, len(rows) - 1)


def main() -> None:
    finance_dirs = [path for path in Path.cwd().iterdir() if path.is_dir()]
    source_names = {
        details[kind]
        for details in PRODUCTS.values()
        for kind in ("data", "schema")
    }
    matches = [
        directory for directory in finance_dirs
        if source_names.intersection(path.name for path in directory.iterdir())
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one finance directory, found {len(matches)}")
    directory = matches[0]

    for product, details in PRODUCTS.items():
        old_data = directory / details["data"]
        old_schema = directory / details["schema"]
        new_data = directory / f"{product}_데이터.csv"
        new_schema = directory / f"{product}_스키마.csv"
        sample = directory / f"{product}_샘플.csv"

        for source in (old_data, old_schema):
            if not source.is_file():
                raise FileNotFoundError(source)
        for destination in (new_data, new_schema, sample):
            if destination.exists():
                raise FileExistsError(destination)

        shutil.move(old_data, new_data)
        shutil.move(old_schema, new_schema)
        sample_rows = create_sample(new_data, sample)
        print(
            f"{product}: 데이터/스키마 이름 변경, "
            f"샘플 {sample_rows}행 생성"
        )


if __name__ == "__main__":
    main()
