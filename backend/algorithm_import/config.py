from __future__ import annotations

import os
from pathlib import Path

DRT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXTERNAL_ALGORITHM_DATA_ROOT = DRT_ROOT.parent / "Herverdelingsalgoritme" / "data"
SUPPORTED_ASSIST_MODES = {"off", "shadow", "rank_assist"}


def get_external_algorithm_data_root() -> Path:
    raw_value = os.getenv("EXTERNAL_ALGORITHM_DATA_ROOT", "").strip()
    if raw_value:
        return Path(raw_value).expanduser()
    return DEFAULT_EXTERNAL_ALGORITHM_DATA_ROOT


def get_algorithm_assist_mode() -> str:
    mode = os.getenv("ALGORITHM_ASSIST_MODE", "off").strip().lower()
    if mode not in SUPPORTED_ASSIST_MODES:
        return "off"
    return mode
