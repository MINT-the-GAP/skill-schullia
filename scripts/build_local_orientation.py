#!/usr/bin/env python3
"""Explicitly build the ignored local orientation metadata index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import local_orientation_config as config
from local_orientation_index import ROOT, IndexFault, build_local_index


class _Parser(argparse.ArgumentParser):
    def error(self, _message):
        raise IndexFault("build_arguments_invalid")


def main(argv: Sequence[str] | None = None) -> int:
    code = 0
    try:
        parser = _Parser(description=__doc__)
        parser.add_argument("--repo-root", type=Path, default=ROOT)
        parser.add_argument("--config", type=Path)
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv)
        payload = build_local_index(args.repo_root, args.config).safe_dict()
    except IndexFault as error:
        code = 1
        payload = {
            "availability_state": error.state, "reason_code": error.code,
            "index_ready": False, "local_search_performed": False,
            "orientation_profile_prepared": False,
            "local_orientation_used": False,
        }
    except Exception:
        code = 2
        payload = {
            "availability_state": config.STATE_EXCLUDED,
            "reason_code": "build_operational_error", "index_ready": False,
            "local_search_performed": False,
            "orientation_profile_prepared": False,
            "local_orientation_used": False,
        }
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
