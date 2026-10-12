"""Optional fail-closed source intake for Personification research consumers.

A host may choose to consume a checked-out source tree. This helper admits only
explicit active paths and rejects historical actor-specific source, traversal,
symlinks and implicit recursive repository loading.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path

_ACTIVE_FILES = frozenset({
    "README.md",
    "PERSONIFICATION_V1.md",
    "src/personification/__init__.py",
    "src/personification/core.py",
    "src/personification/source_policy.py",
})
_MAX_BYTES = 1_000_000


class AdmissionKind(str, Enum):
    ACTIVE = "ACTIVE"
    HISTORICAL = "HISTORICAL"
    NOT_ADMITTED = "NOT_ADMITTED"


def classify_source_path(relative_path: str) -> AdmissionKind:
    if not isinstance(relative_path, str) or not relative_path:
        return AdmissionKind.NOT_ADMITTED
    normalized = relative_path.replace("\\", "/")
    if (normalized.startswith("/") or "//" in normalized
            or ":" in normalized or "\x00" in normalized):
        return AdmissionKind.NOT_ADMITTED
    pieces = normalized.split("/")
    if any(p in ("", ".", "..") for p in pieces):
        return AdmissionKind.NOT_ADMITTED
    if normalized in _ACTIVE_FILES:
        return AdmissionKind.ACTIVE
    if normalized.startswith("history/") or normalized.startswith(
        ("notes/", "vera/", "BRIGIT_")
    ):
        return AdmissionKind.HISTORICAL
    return AdmissionKind.NOT_ADMITTED


def read_active_source(repo_root: Path, relative_path: str) -> str:
    """Return only explicitly admitted current source, never old biographies.

    No caller may load historical documents through this adapter. This does
    not control ungoverned external crawlers, which must separately adopt the
    source admission policy.
    """
    if classify_source_path(relative_path) is not AdmissionKind.ACTIVE:
        raise ValueError("path is not in the active source allowlist")
    root = Path(repo_root).resolve(strict=True)
    path = root.joinpath(*relative_path.replace("\\", "/").split("/"))
    if any(part.is_symlink() for part in [path, *path.parents] if part != root):
        raise ValueError("symbolic links are not admitted")
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("path leaves the source root or is not a file")
    if resolved.stat().st_size > _MAX_BYTES:
        raise ValueError("source file exceeds bounded intake size")
    return resolved.read_text(encoding="utf-8")
