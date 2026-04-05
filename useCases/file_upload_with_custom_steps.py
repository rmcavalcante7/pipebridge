"""
Usage example for extending the upload flow with custom steps.
"""

from __future__ import annotations

import argparse
import random

from pipebridge import FileUploadRequest, UploadConfig
from pipebridge.workflow.config.circuitBreakerConfig import CircuitBreakerConfig
from pipebridge.workflow.config.retryConfig import RetryConfig
from pipebridge.workflow.steps.baseStep import BaseStep
from useCases.common import add_connection_arguments, build_api, print_section


def build_random_txt_file_name() -> str:
    """
    Build a randomized text filename for upload examples.

    :return: str = Randomized ``.txt`` filename
    """
    return f"custom_step_{random.randint(1, 100)}.txt"


class RegisterUseCaseMetadataStep(BaseStep):
    """
    Example custom step that enriches upload context metadata.
    """

    execution_profile = "default"

    def execute(self, context) -> None:
        """
        Register custom metadata before the upload pipeline proceeds.

        :param context: UploadPipelineContext = Shared upload flow context
        """
        context.metadata["use_case"] = "file_upload_with_custom_steps"
        context.metadata["custom_step_executed"] = True


class PrintUploadSummaryStep(BaseStep):
    """
    Example custom step that runs after the built-in upload pipeline.
    """

    execution_profile = "default"

    def execute(self, context) -> None:
        """
        Print a short summary using the enriched upload context.

        :param context: UploadPipelineContext = Shared upload flow context
        """
        print("Custom post-step summary:")
        print(f"- files: {context.files}")
        print(f"- upload_url: {context.upload_url}")
        print(f"- metadata: {context.metadata}")


def main() -> None:
    """
    Execute the upload example with custom steps.
    """
    parser = argparse.ArgumentParser(
        description="Upload a file while injecting custom steps before and after the SDK pipeline.",
    )
    add_connection_arguments(parser)
    parser.add_argument("--card-id", required=True, help="Card identifier.")
    parser.add_argument(
        "--field-id", required=True, help="Attachment field identifier."
    )
    parser.add_argument(
        "--organization-id", required=True, help="Pipefy organization identifier."
    )
    parser.add_argument(
        "--expected-phase-id",
        help="Optional expected current phase identifier.",
    )
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("File Upload With Custom Steps")
    request = FileUploadRequest(
        file_name=build_random_txt_file_name(),
        file_bytes=b"hello from custom-step use case",
        card_id=args.card_id,
        field_id=args.field_id,
        organization_id=args.organization_id,
        replace_files=False,
        expected_phase_id=args.expected_phase_id,
    )

    result = api.files.uploadFile(
        request=request,
        config=UploadConfig(
            retry=RetryConfig(max_retries=3, base_delay=0.5),
            circuit=CircuitBreakerConfig(failure_threshold=3, recovery_timeout=10.0),
        ),
        extra_steps_before=[RegisterUseCaseMetadataStep()],
        extra_steps_after=[PrintUploadSummaryStep()],
    )

    print(result)


if __name__ == "__main__":
    main()
