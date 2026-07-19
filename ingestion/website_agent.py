"""Website path: Firecrawl crawl -> style extraction -> frequency clustering ->
confidence gate -> schema assembly.

The only path that genuinely infers structure from rendered output with no ground
truth. Clustering is frequency-based (deterministic, testable); an optional LLM
step adds semantic names. Confidence is occurrence-driven and gated at `threshold`.
"""
import logging

from ingestion import llm
from ingestion.schema_assembler import DEFAULT_THRESHOLD, assemble, make_token
from tools import firecrawl_tool, style_parser

log = logging.getLogger(__name__)


def cluster(counters, threshold=DEFAULT_THRESHOLD):
    """Turn {category: Counter} into schema token groups with occurrence-based confidence.

    Confidence = occurrences / total-in-category (a value seen everywhere is trusted).
    Below `threshold` -> hitl_status pending, carrying raw observations as evidence.
    """
    groups = {"color": {"primitive": {}}, "typography": {"fontSize": {}, "fontFamily": {}},
              "radius": {}}
    dest = {"color": groups["color"]["primitive"],
            "fontSize": groups["typography"]["fontSize"],
            "fontFamily": groups["typography"]["fontFamily"],
            "radius": groups["radius"]}
    ttype = {"color": "color", "fontSize": "fontSize", "fontFamily": "fontFamily",
             "radius": "dimension"}

    for cat, counter in counters.items():
        total = sum(counter.values()) or 1
        for i, (value, count) in enumerate(counter.most_common()):
            conf = min(1.0, count / total + 0.25)  # frequent values -> higher confidence
            name = f"{cat.lower()}-{i + 1}"
            dest[cat][name] = make_token(
                value, ttype[cat], confidence=conf, threshold=threshold,
                provenance={"occurrence_count": count,
                            "raw_observations": [value]})
    return groups


def _name_semantics(groups, api_key=None):
    """Optional: ask Gemini for semantic color names. Silently skipped if no LLM."""
    if not llm.available():
        return
    try:
        colors = list(groups["color"]["primitive"])
        prompt = ("Given these web color token keys, suggest a semantic role "
                  "(background/text/action/border) for each, one per line as key=role:\n"
                  + "\n".join(colors))
        # ponytail: parsed into descriptions only; keeps naming advisory, never auto-renames.
        for line in llm.call(prompt, api_key=api_key).splitlines():
            if "=" in line:
                k, role = line.split("=", 1)
                tok = groups["color"]["primitive"].get(k.strip())
                if tok:
                    tok["description"] = f"suggested role: {role.strip()}"
    except llm.LLMUnavailable:
        pass


def run(url, config=None):
    config = config or {}
    threshold = config.get("confidence_threshold", DEFAULT_THRESHOLD)
    css_text = firecrawl_tool.scrape(url, api_key=config.get("firecrawl_key"))
    counters = style_parser.extract(css_text)
    groups = cluster(counters, threshold=threshold)
    _name_semantics(groups, api_key=config.get("google_key"))
    return assemble("website", url, groups)
