"""Optional fail-closed source intake for Personification research consumers.

A host may choose to consume a checked-out source tree. This helper admits only
explicit active paths and rejects historical actor-specific source, traversal,
symlinks and implicit recursive repository loading. Intake reads a bounded
opened descriptor, not an unbounded pathname read. Against hostile concurrent
directory mutation, an immutable trusted checkout or platform-specific
directory handle remains necessary; this is not a complete filesystem
transaction or content provenance attestation.
"""
from __future__ import annotations

from enum import Enum
import os
import stat
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
    if normalized.startswith("history/"):
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
    supplied_root = Path(repo_root)
    if supplied_root.is_symlink() or getattr(supplied_root, "is_junction", lambda: False)():
        raise ValueError("linked repository roots are not admitted")
    root = supplied_root.resolve(strict=True)
    path = root.joinpath(*relative_path.replace("\\", "/").split("/"))
    descendants = [path]
    current = path.parent
    while current != root:
        if not current.is_relative_to(root):
            raise ValueError("path leaves the source root")
        descendants.append(current)
        current = current.parent
    if any(part.is_symlink() or getattr(part, "is_junction", lambda: False)()
           for part in descendants):
        raise ValueError("symbolic links and junctions are not admitted")
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("path leaves the source root or is not a file")

    # Read at most the policy bound from the admitted opened descriptor.
    # A prior stat followed by Path.read_text() would allow unbounded growth
    # or file replacement before the unbounded read.
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        current_metadata = path.stat(follow_symlinks=False)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("active source is not a regular file")
        if ((opened.st_dev, opened.st_ino) !=
                (current_metadata.st_dev, current_metadata.st_ino)):
            raise ValueError("active source replaced during admission")
        if opened.st_size > _MAX_BYTES:
            raise ValueError("source exceeds bounded intake size")
        contents = stream.read(_MAX_BYTES + 1)
        if len(contents) > _MAX_BYTES:
            raise ValueError("source exceeds bounded intake size")
        after = os.fstat(stream.fileno())
        if (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError("active source changed during bounded read")
    return contents.decode("utf-8", errors="strict")
