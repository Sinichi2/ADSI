"""Router: LangGraph state graph dispatching to one of the four path modules.

Each source is a graph node wrapping its existing `run(input, config)` — the
graph only owns routing/state, extraction logic is untouched. Public
signature (`dispatch(path, inp, config)`) is unchanged, so callers (main.py,
the Streamlit app) don't need to know a graph is involved.
"""
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from ingestion import manual_wizard
from ingestion.agent import document_agent, figma_agent, website_agent


class IngestState(TypedDict, total=False):
    path: str
    inp: Optional[str]
    config: dict
    doc: dict


def _document(state):
    return {"doc": document_agent.run(state["inp"], state["config"])}


def _figma(state):
    return {"doc": figma_agent.run(state["inp"], state["config"])}


def _website(state):
    return {"doc": website_agent.run(state["inp"], state["config"])}


def _manual(state):
    return {"doc": manual_wizard.run(state["config"])}


_NODES = {"document": _document, "figma": _figma, "website": _website, "manual": _manual}

_graph = StateGraph(IngestState)
for _name, _fn in _NODES.items():
    _graph.add_node(_name, _fn)
    _graph.add_edge(_name, END)
_graph.add_conditional_edges(START, lambda s: s["path"], list(_NODES))
_compiled = _graph.compile()


def dispatch(path, inp=None, config=None):
    if path not in _NODES:
        raise ValueError(f"unknown path '{path}'; choose from {sorted(_NODES)}")
    result = _compiled.invoke({"path": path, "inp": inp, "config": config or {}})
    return result["doc"]
