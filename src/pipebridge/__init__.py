"""
Top-level public API for PipeBridge.

This module intentionally exposes a hybrid public surface:

- the high-level :class:`PipeBridge` facade for most consumers
- the core services for advanced composition scenarios
- the main request/config objects required by upload, update, and move flows
"""

from pipebridge.client.httpClient import PipefyHttpClient
from pipebridge.facade.pipefyFacade import PipeBridge
from pipebridge.models.file.fileDownloadRequest import FileDownloadRequest
from pipebridge.models.file.fileUploadRequest import FileUploadRequest
from pipebridge.service.card.cardService import CardService
from pipebridge.service.card.flows.move.cardMoveConfig import CardMoveConfig
from pipebridge.service.card.flows.update.cardUpdateConfig import CardUpdateConfig
from pipebridge.service.file.fileService import FileService
from pipebridge.service.file.flows.upload.config.uploadConfig import UploadConfig
from pipebridge.service.phase.phaseService import PhaseService
from pipebridge.service.pipe.pipeService import PipeService

__all__ = [
    "PipeBridge",
    "PipefyHttpClient",
    "CardService",
    "FileService",
    "PipeService",
    "PhaseService",
    "FileUploadRequest",
    "FileDownloadRequest",
    "UploadConfig",
    "CardUpdateConfig",
    "CardMoveConfig",
]
