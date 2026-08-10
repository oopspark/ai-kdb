#!/usr/bin/env python3
"""Rebuild each finance sample CSV with reproducible random rows."""

from __future__ import annotations

import csv
import random
from pathlib import Path


PRODUCTS = ["국내채권", "국내ETF", "해외ETF", "공모펀드"]
SAMPLE_SIZE = 100
BASE_SEED = 20260801


def reservoir_sample(
    source: Path, sample_size: int, seed: int
) -> tuple[list[str], list[list[str]], int]:
    rng = random.Random(seed)
    reservoir: list[list[str]] = []

    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        try:
            header = next(reader)
        except StopIteration as error:
            raise ValueError(f"Empty CSV: {source}") from error

        row_count = 0
        for row_count, row in enumerate(reader, start=1):
            if row_count <= sample_size:
                reservoir.append(row)
                continue
            replacement = rng.randrange(row_count)
            if replacement < sample_size:
                reservoir[replacement] = row

    rng.shuffle(reservoir)
    return header, reservoir, row_count


def locate_data_directory(root: Path) -> Path:
    matches = [
        path.parent
        for path in root.rglob("국내채권_데이터.csv")
        if "0_원본파일" not in path.parts
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one processed data directory: {matches}")
    return matches[0]


def main() -> None:
    directory = locate_data_directory(Path.cwd())
    for offset, product in enumerate(PRODUCTS):
        source = directory / f"{product}_데이터.csv"
        destination = directory / f"{product}_샘플.csv"
        header, rows, total_rows = reservoir_sample(
            source, SAMPLE_SIZE, BASE_SEED + offset
        )
        with destination.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(rows)
        print(
            f"{product}: total={total_rows:,}, sampled={len(rows)}, "
            f"seed={BASE_SEED + offset}"
        )


if __name__ == "__main__":
    main()
