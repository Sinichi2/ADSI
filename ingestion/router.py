"""Router: dispatch to one of the four path modules. All expose run(input, config)."""
from ingestion import document_agent, figma_agent, manual_wizard, website_agent

_PATHS = {
    "document": lambda inp, cfg: document_agent.run(inp, cfg),
    "figma": lambda inp, cfg: figma_agent.run(inp, cfg),
    "website": lambda inp, cfg: website_agent.run(inp, cfg),
    "manual": lambda inp, cfg: manual_wizard.run(cfg),
}


def dispatch(path, inp=None, config=None):
    if path not in _PATHS:
        raise ValueError(f"unknown path '{path}'; choose from {sorted(_PATHS)}")
    return _PATHS[path](inp, config or {})
