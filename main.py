"""CLI entry point. Subcommands: document | figma | website | manual.

  python main.py document --file ./spec.pdf --output ./output/tokens.json
  python main.py figma    --file-key <key>  --output ./output/tokens.json
  python main.py website  --url https://example.com --output ./output/tokens.json --confidence-threshold 0.75
  python main.py manual   --output ./output/tokens.json
"""
import argparse
import json
import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from ingestion import hitl_export, router
from ingestion.schema_assembler import iter_tokens

log = logging.getLogger("adsi")


def _config(args):
    return {
        "confidence_threshold": getattr(args, "confidence_threshold", 0.75),
        "firecrawl_key": os.getenv("FIRECRAWL_API_KEY"),
        "google_key": os.getenv("GOOGLE_API_KEY"),
        "figma_token": os.getenv("FIGMA_ACCESS_TOKEN"),
    }


def _log_run(path, doc):
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = os.path.join("runs", ts, path)
    os.makedirs(d, exist_ok=True)
    _write(os.path.join(d, "tokens.json"), doc)


def _write(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def _run(path, inp, args):
    doc = router.dispatch(path, inp, _config(args))
    _write(args.output, doc)
    _log_run(path, doc)
    hitl = hitl_export.build(doc)
    msg = f"Wrote {args.output} ({sum(1 for _ in iter_tokens(doc))} tokens)."
    if hitl["review_items"]:
        hpath = os.path.splitext(args.output)[0] + ".hitl.json"
        _write(hpath, hitl)
        msg += f" {len(hitl['review_items'])} tokens need review -> {hpath}"
    print(msg)


def _out(parser, default=None):
    parser.add_argument("--output", default=default, required=default is None)


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    load_dotenv()
    p = argparse.ArgumentParser(description="Agentic Design System Integration")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("document"); d.add_argument("--file", required=True, dest="inp"); _out(d)
    f = sub.add_parser("figma"); f.add_argument("--file-key", required=True, dest="inp"); _out(f)
    w = sub.add_parser("website"); w.add_argument("--url", required=True, dest="inp")
    w.add_argument("--confidence-threshold", type=float, default=0.75); _out(w)
    m = sub.add_parser("manual"); _out(m, default="./output/tokens.json")

    args = p.parse_args(argv)
    _run(args.cmd, getattr(args, "inp", None), args)


if __name__ == "__main__":
    main()
