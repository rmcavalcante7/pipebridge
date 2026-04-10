"""
Unit tests for transport configuration wiring.
"""

from __future__ import annotations

import pytest
import requests  # type: ignore[import-untyped]

from pipebridge.client import httpClient
from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.client.transportConfig import TransportConfig
from pipebridge.exceptions import ConnectionRequestError, TimeoutRequestError
from pipebridge.facade.pipefyFacade import PipeBridge
from pipebridge.service.card.cardService import CardService


@pytest.mark.unit
def test_transport_config_resolves_verify_from_ca_bundle() -> None:
    """
    Validate verify resolution precedence.
    """
    config = TransportConfig(
        verify_ssl=False,
        ca_bundle_path="C:/certs/company.pem",
    )

    assert config.resolveVerifyValue() == "C:/certs/company.pem"


@pytest.mark.unit
def test_transport_config_default_verify_is_true() -> None:
    """
    Validate the safe default verify behavior.
    """
    config = TransportConfig()

    assert config.resolveVerifyValue() is True


@pytest.mark.unit
def test_http_client_keeps_effective_transport_config() -> None:
    """
    Validate client wiring of transport config.
    """
    config = TransportConfig(timeout=45, verify_ssl=False)

    client = PipefyHttpClient(
        auth_key="token",
        base_url="https://app.pipefy.com/queries",
        transport_config=config,
    )

    assert client.transport_config.timeout == 45
    assert client.transport_config.resolveVerifyValue() is False


@pytest.mark.unit
def test_pipebridge_accepts_transport_config() -> None:
    """
    Validate facade wiring of transport config.
    """
    config = TransportConfig(timeout=50, verify_ssl=False)

    api = PipeBridge(
        token="token",
        base_url="https://app.pipefy.com/queries",
        transport_config=config,
    )

    assert api.transport_config.timeout == 50
    assert api.transport_config.resolveVerifyValue() is False


class DummyResponse:
    """
    Minimal fake response object for transport tests.
    """

    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


@pytest.mark.unit
def test_http_client_retries_connection_error_and_recovers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Validate retry recovery for transient connection failures.
    """
    calls = {"count": 0}

    def fake_post(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise requests.ConnectionError("temporary connection failure")
        return DummyResponse({"data": {"ok": True}})

    monkeypatch.setattr(httpClient.requests, "post", fake_post)

    client = PipefyHttpClient(
        auth_key="token",
        base_url="https://app.pipefy.com/queries",
        transport_config=TransportConfig(
            max_retries=1,
            retry_delay_seconds=0.0,
        ),
    )

    response = client.sendRequest("{ me { id } }")

    assert response == {"data": {"ok": True}}
    assert calls["count"] == 2


@pytest.mark.unit
def test_http_client_retries_timeout_and_exhausts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Validate retry exhaustion for timeout failures.
    """
    calls = {"count": 0}

    def fake_post(*args, **kwargs):
        calls["count"] += 1
        raise requests.Timeout("timeout")

    monkeypatch.setattr(httpClient.requests, "post", fake_post)

    client = PipefyHttpClient(
        auth_key="token",
        base_url="https://app.pipefy.com/queries",
        transport_config=TransportConfig(
            max_retries=2,
            retry_delay_seconds=0.0,
        ),
    )

    with pytest.raises(TimeoutRequestError):
        client.sendRequest("{ me { id } }")

    assert calls["count"] == 3


@pytest.mark.unit
def test_http_client_does_not_retry_generic_request_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Validate that non-transient generic request exceptions do not enter retry.
    """
    calls = {"count": 0}

    def fake_post(*args, **kwargs):
        calls["count"] += 1
        raise requests.RequestException("ssl protocol mismatch")

    monkeypatch.setattr(httpClient.requests, "post", fake_post)

    client = PipefyHttpClient(
        auth_key="token",
        base_url="https://app.pipefy.com/queries",
        transport_config=TransportConfig(
            max_retries=3,
            retry_delay_seconds=0.0,
        ),
    )

    with pytest.raises(Exception):
        client.sendRequest("{ me { id } }")

    assert calls["count"] == 1


@pytest.mark.unit
def test_http_client_applies_verify_and_timeout_from_transport_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Validate propagation of timeout and verify options to requests.post.
    """
    observed: dict = {}

    def fake_post(*args, **kwargs):
        observed.update(kwargs)
        return DummyResponse({"data": {"ok": True}})

    monkeypatch.setattr(httpClient.requests, "post", fake_post)

    client = PipefyHttpClient(
        auth_key="token",
        base_url="https://app.pipefy.com/queries",
        transport_config=TransportConfig(
            timeout=77,
            ca_bundle_path="C:/certs/company.pem",
        ),
    )

    client.sendRequest("{ me { id } }")

    assert observed["timeout"] == 77
    assert observed["verify"] == "C:/certs/company.pem"


@pytest.mark.unit
def test_service_operations_use_custom_transport_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Validate that a custom transport timeout overrides legacy service defaults.
    """
    observed: dict = {}

    def fake_post(*args, **kwargs):
        observed.update(kwargs)
        return DummyResponse({"data": {"createCard": {"card": {"id": "1"}}}})

    monkeypatch.setattr(httpClient.requests, "post", fake_post)

    client = PipefyHttpClient(
        auth_key="token",
        base_url="https://app.pipefy.com/queries",
        transport_config=TransportConfig(timeout=19),
    )
    service = CardService(client)

    service.createCard(pipe_id="pipe-1", title="Card", fields={"title": "x"})

    assert observed["timeout"] == 19
