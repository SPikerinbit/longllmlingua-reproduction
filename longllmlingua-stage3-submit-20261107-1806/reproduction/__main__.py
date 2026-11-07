from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

from .api import APIError
from .common import load_config


def main():
    parser = argparse.ArgumentParser(description="LongLLMLingua stage-one baseline reproduction")
    parser.add_argument("--config", help="JSON config path (default: configs/stage1.json)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare", help="Download pinned data/source references/tokenizer; no API calls")
    sub.add_parser("plan", help="Offline full matrix budget check; no API calls")
    sub.add_parser("check", help="Check config and key presence; no API calls")
    run_parser = sub.add_parser("run", help="Run/resume real baseline API requests")
    run_parser.add_argument("--limit", type=int, help="Max new logical API calls in this invocation")
    summary = sub.add_parser("summarize", help="Rescore saved predictions without API calls")
    summary.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if args.command == "prepare":
            from .data import prepare
            prepare()
        elif args.command == "plan":
            from .runner import plan
            print(json.dumps(plan(config), ensure_ascii=False, indent=2))
        elif args.command == "check":
            from .api import get_key
            get_key(config)
            print(f"Config OK; key present (not printed); provider={config['provider']}; model={config['model']}")
        elif args.command == "run":
            from .runner import run
            _, complete = run(config, args.limit)
            return 0 if complete else 2
        elif args.command == "summarize":
            from .evaluation import summarize
            print(json.dumps(summarize(args.run_dir), ensure_ascii=False, indent=2))
    except (APIError, ValueError, OSError, httpx.HTTPError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
