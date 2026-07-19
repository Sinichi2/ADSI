from ingestion import hitl_export
from ingestion.schema_assembler import assemble, hitl_status_for, make_token


def test_confidence_gate():
    assert hitl_status_for(1.0) == "not_required"
    assert hitl_status_for(0.9) == "not_required"
    assert hitl_status_for(0.5) == "pending"


def test_assemble_valid_and_requires_hitl():
    groups = {
        "color": {"primitive": {
            "blue": make_token("#3b82f6", "color", confidence=1.0),
            "guess": make_token("#123456", "color", confidence=0.4),  # -> pending
        }},
        "spacing": {"sm": make_token("8px", "dimension")},
    }
    doc = assemble("manual", "unit-test", groups)
    assert doc["$meta"]["source_type"] == "manual"
    assert doc["$meta"]["requires_hitl"] is True
    assert doc["color"]["primitive"]["guess"]["hitl_status"] == "pending"


def test_hitl_export_collects_pending_only():
    groups = {"color": {"primitive": {
        "ok": make_token("#000000", "color", confidence=1.0),
        "bad": make_token("#ffffff", "color", confidence=0.3),
    }}}
    doc = assemble("website", "http://x", groups)
    payload = hitl_export.build(doc)
    paths = [i["token_path"] for i in payload["review_items"]]
    assert paths == ["color.primitive.bad"]
