#!/usr/bin/env python3
"""Update schema CSVs with metadata already calculated in the YAML file."""

from __future__ import annotations

import csv
import json
import tempfile
import unicodedata
from pathlib import Path


PRODUCTS = ["국내채권", "국내ETF", "해외ETF", "공모펀드"]
OUTPUT_HEADER = [
    "컬럼명",
    "컬럼영문풀네임",
    "PK/FK",
    "컬럼타입",
    "컬럼한글명",
    "컬럼값 예시",
    "고유값 개수",
    "NULL값 개수",
]


def normalized(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def locate_file(directory: Path, expected_name: str) -> Path:
    matches = [
        path for path in directory.iterdir()
        if path.is_file() and normalized(path.name) == expected_name
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {expected_name}: {matches}")
    return matches[0]


def parse_metadata_yaml(path: Path) -> dict[str, dict[str, dict[str, object]]]:
    """Parse the constrained YAML emitted by build_unique_values_yaml.py."""
    result: dict[str, dict[str, dict[str, object]]] = {}
    current_product: str | None = None
    current_column: str | None = None

    with path.open(encoding="utf-8") as stream:
        for raw_line in stream:
            line = raw_line.rstrip("\n")
            if not line or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            stripped = line.strip()

            if indent == 0 and stripped.endswith(":"):
                current_product = json.loads(stripped[:-1])
                result[current_product] = {}
                current_column = None
            elif indent == 2 and stripped.endswith(":"):
                if current_product is None:
                    raise ValueError("Column found before product")
                current_column = json.loads(stripped[:-1])
                result[current_product][current_column] = {}
            elif indent == 4 and ": " in stripped:
                if current_product is None or current_column is None:
                    raise ValueError("Metadata found before column")
                key, raw_value = stripped.split(": ", 1)
                if key in {"count", "null_count"}:
                    value: object = int(raw_value)
                elif key in {"english_full_name", "korean_name"}:
                    value = json.loads(raw_value)
                else:
                    continue
                result[current_product][current_column][key] = value
    return result


def row_value(row: list[str], positions: dict[str, int], name: str) -> str:
    index = positions.get(name)
    return row[index] if index is not None and index < len(row) else ""


def update_schema(
    schema_path: Path,
    product_metadata: dict[str, dict[str, object]],
) -> int:
    with schema_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream))
    if not rows:
        raise ValueError(f"Invalid schema: {schema_path}")

    header_matches = [
        index for index, row in enumerate(rows) if "컬럼명" in row
    ]
    if len(header_matches) != 1:
        raise ValueError(f"Could not identify one header row: {schema_path}")
    header_index = header_matches[0]
    positions = {
        name: index for index, name in enumerate(rows[header_index])
    }
    if "컬럼명" not in positions:
        raise ValueError(f"Missing 컬럼명: {schema_path}")

    output = [*rows[:header_index], OUTPUT_HEADER]
    for row in rows[header_index + 1:]:
        column = row_value(row, positions, "컬럼명")
        metadata = product_metadata.get(column)
        if metadata is None:
            raise ValueError(f"YAML metadata missing: {schema_path.name}.{column}")
        required = {"english_full_name", "count", "null_count"}
        if not required.issubset(metadata):
            raise ValueError(f"Incomplete YAML metadata: {schema_path.name}.{column}")

        korean_name = row_value(row, positions, "컬럼한글명")
        if not korean_name:
            korean_name = str(metadata.get("korean_name", ""))
        output.append([
            column,
            str(metadata["english_full_name"]),
            row_value(row, positions, "PK/FK"),
            row_value(row, positions, "컬럼타입"),
            korean_name,
            row_value(row, positions, "컬럼값 예시"),
            str(metadata["count"]),
            str(metadata["null_count"]),
        ])

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8-sig",
        newline="",
        dir=schema_path.parent,
        prefix=f".{schema_path.stem}_",
        suffix=".tmp",
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        csv.writer(stream, lineterminator="\n").writerows(output)
    temporary.replace(schema_path)
    return len(rows) - header_index - 1


def main() -> None:
    root = Path.cwd()
    yaml_matches = list(root.rglob("금융상품_컬럼별_고유값.yaml"))
    if len(yaml_matches) != 1:
        raise RuntimeError(f"Expected one metadata YAML: {yaml_matches}")
    yaml_path = yaml_matches[0]
    directory = yaml_path.parent
    metadata = parse_metadata_yaml(yaml_path)

    for product in PRODUCTS:
        schema_path = locate_file(directory, f"{product}_스키마.csv")
        count = update_schema(schema_path, metadata[product])
        print(f"{product}: updated {count} schema columns")


if __name__ == "__main__":
    main()
