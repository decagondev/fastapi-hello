#!/usr/bin/env python3
"""Fail the build if the layering rules in docs/ARCHITECTURE.md are violated.

Dependencies must point inwards::

    api -> services -> domain <- infrastructure

This parses the AST of every module under ``src/app`` rather than grepping, so
it is not fooled by imports inside functions, aliased imports, or comments.

Run directly (``python scripts/check_architecture.py``) or via ``make arch``.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent / "src" / "app"

# layer -> packages it is forbidden to import from
FORBIDDEN: dict[str, frozenset[str]] = {
    "domain": frozenset({"api", "services", "infrastructure", "core", "schemas", "middleware"}),
    "services": frozenset({"api", "core", "schemas", "middleware", "infrastructure"}),
    "infrastructure": frozenset({"api", "services", "core", "schemas", "middleware"}),
}

# layer -> third-party packages it is forbidden to import at all
FORBIDDEN_EXTERNAL: dict[str, frozenset[str]] = {
    "domain": frozenset({"fastapi", "starlette", "pydantic", "pydantic_settings", "uvicorn"}),
    "services": frozenset({"fastapi", "starlette", "uvicorn"}),
}


def layer_of(path: Path) -> str | None:
    """Return the top-level package name a module belongs to."""
    relative = path.relative_to(PACKAGE_ROOT)
    return relative.parts[0] if len(relative.parts) > 1 else None


def imported_modules(tree: ast.AST) -> set[str]:
    """Return every module name imported anywhere in the file."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module)
    return found


def violations() -> list[str]:
    """Return a human-readable list of every layering violation found."""
    problems: list[str] = []

    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        layer = layer_of(path)
        if layer is None:
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        location = path.relative_to(PACKAGE_ROOT.parent.parent)

        for module in sorted(imported_modules(tree)):
            root = module.split(".")[0]

            if root in FORBIDDEN_EXTERNAL.get(layer, frozenset()):
                problems.append(f"{location}: '{layer}' must not import '{module}'")

            if root == "app":
                target = module.split(".")[1] if module.count(".") >= 1 else ""
                if target in FORBIDDEN.get(layer, frozenset()):
                    problems.append(
                        f"{location}: '{layer}' must not import from 'app.{target}' "
                        f"(dependencies point inwards)"
                    )

    return problems


def main() -> int:
    """Print any violations and return a process exit code."""
    problems = violations()
    if problems:
        print("Architecture violations found:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print("\nSee docs/ARCHITECTURE.md for the layering rules.", file=sys.stderr)
        return 1
    print("Architecture OK: dependencies point inwards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
