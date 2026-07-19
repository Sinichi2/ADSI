from ingestion.figma_agent import map_variables

# Fixture: two collections (colors single-mode, spacing) + a broken alias.
FIXTURE = {"meta": {
    "variableCollections": {
        "c1": {"defaultModeId": "m1", "name": "Colors",
               "modes": [{"modeId": "m1", "name": "light"}, {"modeId": "m2", "name": "dark"}]},
        "c2": {"defaultModeId": "s1", "name": "Spacing",
               "modes": [{"modeId": "s1", "name": "base"}]},
    },
    "variables": {
        "v1": {"name": "brand/blue", "resolvedType": "COLOR", "variableCollectionId": "c1",
               "valuesByMode": {"m1": {"r": 0.2, "g": 0.5, "b": 0.9, "a": 1}}},
        "v2": {"name": "space/md", "resolvedType": "FLOAT", "variableCollectionId": "c2",
               "valuesByMode": {"s1": 16}},
        "v3": {"name": "broken", "resolvedType": "COLOR", "variableCollectionId": "c1",
               "valuesByMode": {"m1": {"type": "VARIABLE_ALIAS", "id": "VariableID:9:9"}}},
    },
}}


def test_color_float_and_broken_alias():
    groups, modes = map_variables(FIXTURE)
    assert groups["color"]["primitive"]["brand-blue"]["value"] == "#3380e6"
    assert groups["color"]["primitive"]["brand-blue"]["confidence"] == 1.0
    assert groups["spacing"]["space-md"]["value"] == "16px"
    broken = groups["color"]["primitive"]["broken"]
    assert broken["hitl_status"] == "pending"
    assert broken["provenance"]["alias_chain"] == ["VariableID:9:9"]
    assert set(modes) == {"light", "dark", "base"}
