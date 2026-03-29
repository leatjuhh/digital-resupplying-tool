from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ArtifactReadError(Exception):
    path: Path
    reason: str

    def __str__(self) -> str:
        return f"{self.reason}: {self.path}"


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat()


def artifact_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ArtifactReadError(path=path, reason="Artefact ontbreekt")

    content = path.read_bytes()
    stat = path.stat()
    return {
        "source_path": str(path),
        "size_bytes": stat.st_size,
        "modified_at": _iso(datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def read_json_artifact(path: Path, *, required: bool = True) -> tuple[Any | None, dict[str, Any] | None]:
    if not path.exists():
        if required:
            raise ArtifactReadError(path=path, reason="Artefact ontbreekt")
        return None, None

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ArtifactReadError(path=path, reason=f"Artefact kon niet gelezen worden ({exc})") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ArtifactReadError(path=path, reason=f"Ongeldige JSON ({exc})") from exc

    return payload, artifact_metadata(path)


def list_available_years(data_root: Path) -> list[int]:
    if not data_root.exists():
        return []
    years = []
    for child in data_root.iterdir():
        if child.is_dir() and child.name.isdigit():
            years.append(int(child.name))
    return sorted(years)


def list_available_weeks(data_root: Path, year: int) -> list[int]:
    year_dir = data_root / str(year)
    if not year_dir.exists():
        return []

    weeks = []
    for child in year_dir.iterdir():
        if child.is_dir() and child.name.startswith("week_"):
            try:
                weeks.append(int(child.name.split("_", 1)[1]))
            except ValueError:
                continue
    return sorted(weeks)


def week_dir(data_root: Path, year: int, week: int) -> Path:
    return data_root / str(year) / f"week_{week}"


def aggregate_dir(data_root: Path, year: int) -> Path:
    return data_root / str(year) / "aggregate"
