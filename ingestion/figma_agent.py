"""Figma path: deterministic mapping of local variables -> canonical tokens.

Most reliable path — variables are already human-named and structured. All tokens
get confidence 1.0 / not_required, except variables whose alias/mode fails to
resolve, which are flagged pending with an explanatory note.
"""
from ingestion.schema_assembler import assemble, make_token


def _rgba_to_hex(v):
    r, g, b = (round(v[k] * 255) for k in ("r", "g", "b"))
    a = v.get("a", 1)
    hexv = f"#{r:02x}{g:02x}{b:02x}"
    return hexv if a >= 1 else hexv + f"{round(a * 255):02x}"


def _float_category(collection_name):
    n = (collection_name or "").lower()
    if "spac" in n:
        return "spacing", "dimension"
    if "radi" in n or "corner" in n:
        return "radius", "dimension"
    return "spacing", "dimension"  # default numeric collection -> spacing


def map_variables(payload):
    """Turn a /variables/local response into (groups, modes). Pure — unit-testable."""
    meta = payload.get("meta", payload)
    variables = meta.get("variables", {})
    collections = meta.get("variableCollections", {})

    groups = {"color": {"primitive": {}}, "typography": {"fontFamily": {}},
              "spacing": {}, "radius": {}}
    modes = set()

    for var in variables.values():
        name = var["name"].replace("/", "-")
        coll = collections.get(var.get("variableCollectionId"), {})
        coll_modes = {m["modeId"]: m["name"] for m in coll.get("modes", [])}
        modes.update(coll_modes.values())
        vals = var.get("valuesByMode", {})
        if not vals:
            continue
        mode_id = coll.get("defaultModeId") or next(iter(vals))
        raw = vals.get(mode_id)

        rtype = var.get("resolvedType")

        # Broken alias / unresolved mode -> pending with the alias chain as evidence.
        if isinstance(raw, dict) and raw.get("type") == "VARIABLE_ALIAS":
            ttype = {"COLOR": "color", "FLOAT": "dimension", "STRING": "fontFamily"}.get(rtype, "color")
            groups["color"]["primitive"][name] = make_token(
                None, ttype, hitl_status="pending",
                description="Unresolved Figma alias",
                provenance={"alias_chain": [raw.get("id", "?")]})
            continue

        if rtype == "COLOR":
            groups["color"]["primitive"][name] = make_token(_rgba_to_hex(raw), "color")
        elif rtype == "FLOAT":
            cat, ttype = _float_category(coll.get("name"))
            groups[cat][name] = make_token(f"{raw}px", ttype)
        elif rtype == "STRING":
            groups["typography"]["fontFamily"][name] = make_token(raw, "fontFamily")
        # BOOLEAN and unknowns are skipped — not design tokens.

    return groups, sorted(modes)


def run(file_key, config=None):
    from tools import figma_client  # lazy: figma path only, keeps it optional
    config = config or {}
    payload = figma_client.get_local_variables(file_key, token=config.get("figma_token"))
    groups, modes = map_variables(payload)
    return assemble("figma", file_key, groups, modes=modes)
