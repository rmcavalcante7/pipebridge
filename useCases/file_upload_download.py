"""
Usage example for file upload and download through the public SDK facade.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from pipebridge import FileDownloadRequest, FileUploadRequest, UploadConfig
from pipebridge.workflow.config.circuitBreakerConfig import CircuitBreakerConfig
from pipebridge.workflow.config.retryConfig import RetryConfig
from useCases.common import add_connection_arguments, build_api, print_section


def build_random_txt_file_name() -> str:
    """
    Build a randomized text filename for upload examples.

    :return: str = Randomized ``.txt`` filename
    """
    return f"example_{random.randint(1, 100)}.txt"


def main() -> None:
    """
    Execute the file upload and download example.
    """
    parser = argparse.ArgumentParser(
        description="Upload a file to a card field and optionally download attachments back.",
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
        help="Optional expected current phase identifier for safer uploads.",
    )
    parser.add_argument(
        "--download-output-dir",
        help="Optional directory to download all attachments after upload.",
    )
    args = parser.parse_args()

    api = build_api(token=args.token, base_url=args.base_url)

    print_section("Upload File")
    upload_request = FileUploadRequest(
        file_name=build_random_txt_file_name(),
        file_bytes=b"hello from pipebridge sdk use case",
        card_id=args.card_id,
        field_id=args.field_id,
        organization_id=args.organization_id,
        replace_files=False,
        expected_phase_id=args.expected_phase_id,
    )

    upload_result = api.files.uploadFile(
        request=upload_request,
        config=UploadConfig(
            retry=RetryConfig(max_retries=3, base_delay=0.5),
            circuit=CircuitBreakerConfig(failure_threshold=3, recovery_timeout=10.0),
        ),
    )

    print(upload_result)

    if args.download_output_dir:
        print_section("Download Attachments")
        output_dir = Path(args.download_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        download_request = FileDownloadRequest(
            card_id=args.card_id,
            field_id=args.field_id,
            output_dir=str(output_dir),
        )
        files = api.files.downloadAllAttachments(download_request)
        for file_path in files:
            print(file_path)


if __name__ == "__main__":
    main()
