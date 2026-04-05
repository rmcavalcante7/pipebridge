"""
Usage example for file upload with custom rules and execution policies.
"""

from __future__ import annotations

import argparse
import random

from pipebridge import FileUploadRequest, UploadConfig
from pipebridge.exceptions import ValidationError
from pipebridge.workflow.config.circuitBreakerConfig import CircuitBreakerConfig
from pipebridge.workflow.config.retryConfig import RetryConfig
from pipebridge.workflow.rules.baseRule import BaseRule
from useCases.common import add_connection_arguments, build_api, print_section


def build_random_txt_file_name() -> str:
    """
    Build a randomized text filename for upload examples.

    :return: str = Randomized ``.txt`` filename
    """
    return f"custom_rule_{random.randint(1, 100)}.txt"


class FileNamePrefixRule(BaseRule):
    """
    Example custom upload rule that enforces a filename prefix.
    """

    def __init__(self, required_prefix: str) -> None:
        """
        Initialize the prefix validation rule.

        :param required_prefix: str = Required file name prefix
        """
        self.required_prefix = required_prefix

    def execute(self, context) -> None:
        """
        Validate that the upload file name starts with the required prefix.

        :param context: UploadPipelineContext = Shared upload context

        :raises ValidationError:
            When the file name does not match the configured prefix
        """
        file_name = context.request.file_name
        if not file_name.startswith(self.required_prefix):
            raise ValidationError(
                message=(
                    f"Upload file name must start with '{self.required_prefix}'. "
                    f"Received '{file_name}'."
                ),
                class_name=self.__class__.__name__,
                method_name="execute",
            )


def main() -> None:
    """
    Execute the upload example with custom rules and policies.
    """
    parser = argparse.ArgumentParser(
        description="Upload a file using custom validation rules and explicit retry/circuit policies.",
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
    parser.add_argument(
        "--required-prefix",
        default="custom_rule_",
        help="Required prefix enforced by the custom rule.",
    )
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("File Upload With Rules And Policies")
    request = FileUploadRequest(
        file_name=build_random_txt_file_name(),
        file_bytes=b"hello from advanced upload use case",
        card_id=args.card_id,
        field_id=args.field_id,
        organization_id=args.organization_id,
        replace_files=False,
        expected_phase_id=args.expected_phase_id,
    )

    result = api.files.uploadFile(
        request=request,
        extra_rules=[FileNamePrefixRule(args.required_prefix)],
        config=UploadConfig(
            retry=RetryConfig(max_retries=5, base_delay=1.0),
            circuit=CircuitBreakerConfig(failure_threshold=5, recovery_timeout=5.0),
        ),
    )

    print(result)


if __name__ == "__main__":
    main()
