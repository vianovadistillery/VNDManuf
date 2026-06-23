#!/usr/bin/env python3
"""Update CRM_Summary.docx timeline table: two rows per entry (visit + comment)."""

from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "CRM_Summary.docx"


def main() -> None:
    doc = Document(TEMPLATE)
    table = doc.tables[2]

    while len(table.rows) < 4:
        table.add_row()

    table.rows[1].cells[0].text = "{% for item in timeline_items %}{{ item.when }}"
    table.rows[1].cells[1].text = "{{ item.type }}"
    table.rows[1].cells[2].text = "{{ item.title }}"
    table.rows[1].cells[3].text = "{{ item.source }}"

    comment_cell = table.rows[2].cells[0]
    comment_cell.merge(table.rows[2].cells[1])
    comment_cell.merge(table.rows[2].cells[2])
    comment_cell.merge(table.rows[2].cells[3])
    comment_cell.text = "{{ item.comment }}"

    table.rows[3].cells[0].text = "{% endfor %}"
    for ci in range(1, 4):
        table.rows[3].cells[ci].text = ""

    try:
        doc.save(TEMPLATE)
        print(f"Updated {TEMPLATE}")
    except PermissionError:
        fallback = TEMPLATE.with_name("CRM_Summary_timeline2row.docx")
        doc.save(fallback)
        print(f"Could not write {TEMPLATE} (file open?) — saved {fallback}")
        print("Close Word and copy/rename to CRM_Summary.docx, or re-run this script.")


if __name__ == "__main__":
    main()
