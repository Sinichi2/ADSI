import openpyxl

from ingestion.document_agent import parse_excel


def _make_xlsx(path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "color"
    ws.append(["name", "color"])
    ws.append(["blue-500", "#3b82f6"])
    ws.append(["red-500", "#ef4444"])
    sp = wb.create_sheet("spacing")
    sp.append(["name", "spacing"])
    sp.append(["sm", "8px"])
    wb.save(path)


def test_parse_excel_explicit_values(tmp_path):
    xlsx = tmp_path / "spec.xlsx"
    _make_xlsx(str(xlsx))
    groups = parse_excel(str(xlsx))
    blue = groups["color"]["primitive"]["blue-500"]
    assert blue["value"] == "#3b82f6"
    assert blue["confidence"] == 1.0
    assert blue["hitl_status"] == "not_required"
    assert groups["spacing"]["sm"]["value"] == "8px"
