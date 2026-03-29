from __future__ import annotations

import os
from pathlib import Path

DEFAULT_EXTERNAL_ALGORITHM_DATA_ROOT = Path(
    r"C:\Users\Alain\OneDrive\Werk\.codex projecten\Herverdelingsalgoritme\data"
)
SUPPORTED_ASSIST_MODES = {"off", "shadow", "rank_assist"}


def get_external_algorithm_data_root() -> Path:
    raw_value = os.getenv("EXTERNAL_ALGORITHM_DATA_ROOT")
    if raw_value:
        return Path(raw_value)
    return DEFAULT_EXTERNAL_ALGORITHM_DATA_ROOT


def get_algorithm_assist_mode() -> str:
    mode = os.getenv("ALGORITHM_ASSIST_MODE", "off").strip().lower()
    if mode not in SUPPORTED_ASSIST_MODES:
        return "off"
    return mode
