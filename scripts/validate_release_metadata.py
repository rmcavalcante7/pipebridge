from __future__ import annotations

import argparse
import pathlib
import re
import sys
import tarfile
import tomllib
import zipfile


def fail(message: str) -> None:
    print(f"[release-validation] {message}", file=sys.stderr)
    raise SystemExit(1)


def load_repository_url(pyproject_path: pathlib.Path) -> str:
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    try:
        return data["project"]["urls"]["Repository"].rstrip("/")
    except KeyError as exc:
        fail(f"Unable to read project.urls.Repository from {pyproject_path}: {exc}")


def validate_readme(readme_path: pathlib.Path, repository_url: str, tag: str) -> None:
    readme = readme_path.read_text(encoding="utf-8")
    required_fragments = {
        "release link": f"{repository_url}/releases/tag/{tag}",
        "release badge": f"badge/tag-{tag}-",
        "release highlight": f"New in `{tag}`",
    }

    missing = [
        f"{label}: {fragment}"
        for label, fragment in required_fragments.items()
        if fragment not in readme
    ]
    if missing:
        fail(
            "README.md is not aligned with the release tag. Missing fragments: "
            + "; ".join(missing)
        )


def extract_wheel_version(wheel_path: pathlib.Path) -> str:
    with zipfile.ZipFile(wheel_path) as wheel:
        metadata_name = next(
            (name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")),
            None,
        )
        if metadata_name is None:
            fail(f"Unable to locate wheel metadata inside {wheel_path.name}")
        metadata = wheel.read(metadata_name).decode("utf-8")

    match = re.search(r"^Version:\s+(.+)$", metadata, flags=re.MULTILINE)
    if match is None:
        fail(f"Unable to extract Version from wheel metadata in {wheel_path.name}")
    return match.group(1).strip()


def extract_sdist_version(sdist_path: pathlib.Path) -> str:
    match = re.match(r"^pipebridge-(.+)\.tar\.gz$", sdist_path.name)
    if match is None:
        fail(f"Unexpected sdist filename format: {sdist_path.name}")
    return match.group(1)


def validate_dist(dist_dir: pathlib.Path, expected_version: str) -> None:
    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))

    if len(wheels) != 1:
        fail(f"Expected exactly one wheel in {dist_dir}, found {len(wheels)}")
    if len(sdists) != 1:
        fail(f"Expected exactly one sdist in {dist_dir}, found {len(sdists)}")

    wheel_version = extract_wheel_version(wheels[0])
    sdist_version = extract_sdist_version(sdists[0])

    if wheel_version != expected_version:
        fail(
            f"Wheel version mismatch: expected {expected_version}, found {wheel_version}"
        )
    if sdist_version != expected_version:
        fail(
            f"Sdist version mismatch: expected {expected_version}, found {sdist_version}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate README release tag consistency and built package version."
    )
    parser.add_argument("--tag", required=True, help="Release tag, e.g. v0.2.3")
    parser.add_argument(
        "--readme",
        default="README.md",
        help="Path to the README published on PyPI.",
    )
    parser.add_argument(
        "--pyproject",
        default="pyproject.toml",
        help="Path to pyproject.toml.",
    )
    parser.add_argument(
        "--dist-dir",
        default=None,
        help="Optional dist directory to validate built artifact versions.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.tag.startswith("v"):
        fail(f"Expected a release tag starting with 'v', got {args.tag}")

    expected_version = args.tag.removeprefix("v")
    readme_path = pathlib.Path(args.readme)
    pyproject_path = pathlib.Path(args.pyproject)

    repository_url = load_repository_url(pyproject_path)
    validate_readme(readme_path, repository_url, args.tag)

    if args.dist_dir is not None:
        validate_dist(pathlib.Path(args.dist_dir), expected_version)

    print(
        f"[release-validation] README and package metadata are aligned with {args.tag}"
    )


if __name__ == "__main__":
    main()
