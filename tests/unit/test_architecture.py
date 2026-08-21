"""The layering rules are executable, not just documentation."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

pytestmark = pytest.mark.unit

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_architecture.py"


def _load_checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_architecture", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_no_layering_violations():
    checker = _load_checker()
    assert checker.violations() == []


def test_checker_reports_forbidden_imports():
    """Guards the guard: a rule that cannot fail is not a rule."""
    checker = _load_checker()
    assert "fastapi" in checker.FORBIDDEN_EXTERNAL["domain"]
    assert "infrastructure" in checker.FORBIDDEN["services"]
    assert "api" in checker.FORBIDDEN["domain"]
