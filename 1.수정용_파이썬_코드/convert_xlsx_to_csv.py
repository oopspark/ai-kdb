#!/usr/bin/env python3
"""Convert every .xlsx below a directory to UTF-8 BOM CSV files.

The implementation uses only Python's standard library. Each worksheet is
written separately. Single-sheet workbooks use ``<workbook>.csv``; multi-sheet
workbooks use ``<workbook>__<sheet>.csv``.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN_NS, "r": REL_NS, "p": PKG_REL_NS}
CELL_REF_RE = re.compile(r"([A-Z]+)")
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def column_number(cell_ref: str) -> int:
    match = CELL_REF_RE.match(cell_ref)
    if not match:
        return 1
    result = 0
    for char in match.group(1):
        result = result * 26 + ord(char) - ord("A") + 1
    return result


def safe_filename(value: str) -> str:
    cleaned = INVALID_FILENAME_CHARS.sub("_", value).strip().rstrip(".")
    return cleaned or "Sheet"


def load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        stream = archive.open("xl/sharedStrings.xml")
    except KeyError:
        return []
    strings: list[str] = []
    with stream:
        for event, element in ET.iterparse(stream, events=("end",)):
            if element.tag == f"{{{MAIN_NS}}}si":
                strings.append(
                    "".join(
                        node.text or ""
                        for node in element.iter(f"{{{MAIN_NS}}}t")
                    )
                )
                element.clear()
    return strings


def worksheet_entries(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    with archive.open("xl/workbook.xml") as workbook_stream:
        workbook = ET.parse(workbook_stream)
    with archive.open("xl/_rels/workbook.xml.rels") as rels_stream:
        rels = ET.parse(rels_stream)

    targets = {
        rel.get("Id"): rel.get("Target", "")
        for rel in rels.findall("p:Relationship", NS)
    }
    entries: list[tuple[str, str]] = []
    for sheet in workbook.findall(".//m:sheets/m:sheet", NS):
        relationship_id = sheet.get(f"{{{REL_NS}}}id", "")
        target = targets.get(relationship_id, "")
        if target.startswith("/"):
            path = target.lstrip("/")
        elif target.startswith("xl/"):
            path = target
        else:
            path = f"xl/{target}"
        entries.append((sheet.get("name", "Sheet"), path))
    return entries


def cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.get("t")
    if cell_type == "inlineStr":
        return "".join(
            node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t")
        )

    value_node = cell.find("m:v", NS)
    if value_node is None or value_node.text is None:
        formula_node = cell.find("m:f", NS)
        return f"={formula_node.text}" if formula_node is not None else ""

    raw_value = value_node.text
    if cell_type == "s":
        try:
            return shared_strings[int(raw_value)]
        except (ValueError, IndexError):
            return raw_value
    if cell_type == "b":
        return "TRUE" if raw_value == "1" else "FALSE"
    return raw_value


def convert_sheet(
    archive: zipfile.ZipFile,
    sheet_path: str,
    output_path: Path,
    shared_strings: list[str],
) -> int:
    row_count = 0
    with archive.open(sheet_path) as sheet_stream, output_path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as csv_stream:
        writer = csv.writer(csv_stream, lineterminator="\n")
        for event, element in ET.iterparse(sheet_stream, events=("end",)):
            if element.tag != f"{{{MAIN_NS}}}row":
                continue
            row: list[str] = []
            for cell in element.findall("m:c", NS):
                index = column_number(cell.get("r", "A1"))
                if index > len(row):
                    row.extend([""] * (index - len(row)))
                row[index - 1] = cell_value(cell, shared_strings)
            writer.writerow(row)
            row_count += 1
            element.clear()
    return row_count


def convert_workbook(source: Path) -> list[tuple[Path, int]]:
    completed: list[tuple[Path, int]] = []
    with zipfile.ZipFile(source) as archive:
        shared_strings = load_shared_strings(archive)
        sheets = worksheet_entries(archive)
        multiple_sheets = len(sheets) > 1

        for sheet_name, sheet_path in sheets:
            suffix = f"__{safe_filename(sheet_name)}" if multiple_sheets else ""
            destination = source.with_name(f"{source.stem}{suffix}.csv")
            with tempfile.NamedTemporaryFile(
                dir=source.parent, prefix=f".{source.stem}_", suffix=".tmp",
                delete=False
            ) as temp_file:
                temporary_path = Path(temp_file.name)
            try:
                row_count = convert_sheet(
                    archive, sheet_path, temporary_path, shared_strings
                )
                shutil.move(temporary_path, destination)
            finally:
                temporary_path.unlink(missing_ok=True)
            completed.append((destination, row_count))
    return completed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory", nargs="?", type=Path, default=Path.cwd(),
        help="Directory to scan recursively (default: current directory)",
    )
    args = parser.parse_args()

    sources = sorted(
        path for path in args.directory.rglob("*.xlsx")
        if not path.name.startswith("~$")
    )
    if not sources:
        raise SystemExit("No .xlsx files found.")

    total_csv_files = 0
    for source in sources:
        results = convert_workbook(source)
        for destination, row_count in results:
            print(f"{source} -> {destination} ({row_count:,} rows)")
        total_csv_files += len(results)
    print(f"Converted {len(sources)} workbook(s) into {total_csv_files} CSV file(s).")


if __name__ == "__main__":
    main()
