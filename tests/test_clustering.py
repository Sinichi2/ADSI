from collections import Counter

from ingestion.website_agent import cluster
from tools import style_parser


def test_extract_normalizes_hex_and_counts():
    css = "a{color:#FFF} b{color:#ffffff} c{font-size:16px} d{border-radius:4px}"
    out = style_parser.extract(css)
    assert out["color"]["#ffffff"] == 2  # #FFF expands and merges with #ffffff
    assert out["fontSize"]["16px"] == 1
    assert out["radius"]["4px"] == 1


def test_cluster_gates_low_frequency():
    counters = {"color": Counter({"#000000": 10, "#abcdef": 1})}
    groups = cluster(counters, threshold=0.75)
    toks = groups["color"]["primitive"]
    frequent = next(t for t in toks.values() if t["value"] == "#000000")
    rare = next(t for t in toks.values() if t["value"] == "#abcdef")
    assert frequent["hitl_status"] == "not_required"
    assert rare["hitl_status"] == "pending"
    assert rare["provenance"]["occurrence_count"] == 1
