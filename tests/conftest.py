"""
Shared pytest fixtures and test environment bootstrap.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_configure(config: pytest.Config) -> None:
    """
    Register project-specific test markers.

    :param config: pytest.Config = Active pytest configuration
    """
    config.addinivalue_line(
        "markers",
        "unit: fast isolated tests with no network or external credentials",
    )
    config.addinivalue_line(
        "markers",
        "functional: tests focused on the public SDK API surface",
    )
    config.addinivalue_line(
        "markers",
        "integration: tests that exercise the real Pipefy API and require credentials",
    )


@pytest.fixture()
def project_root() -> Path:
    """
    Return the repository root directory.

    :return: Path = Project root path
    """
    return PROJECT_ROOT


@pytest.fixture()
def src_root() -> Path:
    """
    Return the source root directory.

    :return: Path = Source root path
    """
    return SRC_ROOT


@pytest.fixture()
def live_pipefy_api() -> Any:
    """
    Build a real Pipefy facade for integration tests when credentials exist.

    Credential resolution strategy:
    - ``PIPEFY_API_TOKEN`` environment variable
    - optional ``PIPEFY_BASE_URL`` environment variable

    :return: Pipefy = Initialized real SDK facade

    :raises pytest.skip:
        When live credentials are not available
    """
    from pipebridge import PipeBridge

    base_url = os.getenv("PIPEFY_BASE_URL", "https://app.pipefy.com/queries")
    token = os.getenv("PIPEFY_API_TOKEN")
    if token:
        return PipeBridge(token=token, base_url=base_url)

    pytest.skip(
        "Live Pipefy credentials are unavailable. Define PIPEFY_API_TOKEN "
        "and optionally PIPEFY_BASE_URL to run integration tests."
    )
