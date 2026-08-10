#!/usr/bin/env python3
"""Extract page text and render page images from a PDF."""

from __future__ import annotations

import sys
from pathlib import Path

import fitz


def main() -> None:
    source = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)
    document = fitz.open(source)
    text_parts: list[str] = []
    matrix = fitz.Matrix(1.6, 1.6)

    for number, page in enumerate(document, start=1):
        text_parts.append(f"\n===== PAGE {number} =====\n")
        text_parts.append(page.get_text("text", sort=True))
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        pixmap.save(output_dir / f"page-{number:02d}.png")

    contact = fitz.open()
    sheet_width, sheet_height = 1684, 1190
    margin, gap = 24, 18
    cell_width = (sheet_width - margin * 2 - gap) / 2
    cell_height = (sheet_height - margin * 2 - gap) / 2
    for start in range(0, document.page_count, 4):
        sheet = contact.new_page(width=sheet_width, height=sheet_height)
        for offset in range(4):
            page_index = start + offset
            if page_index >= document.page_count:
                break
            column, row = offset % 2, offset // 2
            rect = fitz.Rect(
                margin + column * (cell_width + gap),
                margin + row * (cell_height + gap),
                margin + column * (cell_width + gap) + cell_width,
                margin + row * (cell_height + gap) + cell_height,
            )
            sheet.show_pdf_page(rect, document, page_index, keep_proportion=True)
    for number, page in enumerate(contact, start=1):
        page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False).save(
            output_dir / f"contact-{number:02d}.png"
        )

    (output_dir / "extracted.txt").write_text(
        "".join(text_parts), encoding="utf-8"
    )
    print(f"pages={document.page_count}")


if __name__ == "__main__":
    main()
