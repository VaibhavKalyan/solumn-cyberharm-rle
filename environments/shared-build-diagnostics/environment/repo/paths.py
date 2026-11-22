"""Constrain build input resolution to the project's source tree."""
from pathlib import Path, PurePosixPath


def source_path(project, relative):
    if not isinstance(relative, str):
        raise ValueError("source path must be a string")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or not parts.parts or parts.parts[0] != "src":
        raise ValueError("source outside src")
    root = Path(project).resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to(root / "src"):
        raise ValueError("source escapes project")
    return target
