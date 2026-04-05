"""
Unit tests for the in-memory pipe schema cache.
"""

from __future__ import annotations

from time import sleep

import pytest

from pipebridge.models.phase import Phase
from pipebridge.models.phaseField import PhaseField
from pipebridge.models.pipe import Pipe
from pipebridge.service.pipe.cache.pipeSchemaCache import PipeSchemaCache


def build_sample_pipe(pipe_id: str = "pipe-1", phase_id: str = "phase-1") -> Pipe:
    """
    Build a minimal modeled pipe schema for cache tests.

    :param pipe_id: str = Pipe identifier
    :param phase_id: str = Phase identifier

    :return: Pipe = Sample modeled pipe
    """
    return Pipe(
        id=pipe_id,
        name="Sample Pipe",
        phases=[
            Phase(
                id=phase_id,
                name="Sample Phase",
                fields=[
                    PhaseField(
                        id="field-1",
                        label="Field 1",
                        type="short_text",
                    )
                ],
            )
        ],
    )


@pytest.mark.unit
def test_cache_store_and_lookup() -> None:
    """
    Validate basic set/get and phase index behavior.
    """
    cache = PipeSchemaCache(ttl_seconds=60)
    pipe = build_sample_pipe()

    cache.set(pipe.id, pipe)

    cached_pipe = cache.get(pipe.id)
    cached_phase = cache.getPhaseSchema("phase-1")
    stats = cache.getStats()

    assert cached_pipe is not None
    assert cached_phase is not None
    assert cached_phase.id == "phase-1"
    assert stats["entries"] == 1
    assert stats["indexed_phases"] == 1


@pytest.mark.unit
def test_cache_expiration() -> None:
    """
    Validate TTL expiration behavior.
    """
    cache = PipeSchemaCache(ttl_seconds=1)
    pipe = build_sample_pipe(pipe_id="pipe-exp")

    cache.set(pipe.id, pipe)
    assert cache.get(pipe.id) is not None

    sleep(1.2)

    assert cache.get(pipe.id) is None
    info = cache.getEntryInfo(pipe.id)
    assert info is not None
    assert info["is_expired"] is True


@pytest.mark.unit
def test_cache_invalidation() -> None:
    """
    Validate targeted and global invalidation.
    """
    cache = PipeSchemaCache(ttl_seconds=60)
    first_pipe = build_sample_pipe(pipe_id="pipe-a", phase_id="phase-a")
    second_pipe = build_sample_pipe(pipe_id="pipe-b", phase_id="phase-b")

    cache.set(first_pipe.id, first_pipe)
    cache.set(second_pipe.id, second_pipe)

    cache.invalidate("pipe-a")
    assert cache.get("pipe-a") is None
    assert cache.getPhaseSchema("phase-a") is None
    assert cache.get("pipe-b") is not None

    cache.invalidateAll()
    stats = cache.getStats()
    assert stats["entries"] == 0
    assert stats["indexed_phases"] == 0


@pytest.mark.unit
def test_cache_get_or_load_only_loads_once() -> None:
    """
    Validate lazy load behavior under a valid cached entry.
    """
    cache = PipeSchemaCache(ttl_seconds=60)
    calls = {"count": 0}

    def loader() -> Pipe:
        calls["count"] += 1
        return build_sample_pipe(pipe_id="pipe-loader", phase_id="phase-loader")

    pipe_one = cache.getOrLoad("pipe-loader", loader)
    pipe_two = cache.getOrLoad("pipe-loader", loader)

    assert pipe_one.id == "pipe-loader"
    assert pipe_two.id == "pipe-loader"
    assert calls["count"] == 1
