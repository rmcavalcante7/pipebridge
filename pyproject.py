import toml
import ast
from pathlib import Path
from importlib.metadata import distributions
import sys
from typing import List, Set

# ============================================================
# CONSTANTS
# ============================================================

STDLIB_MODULES: Set[str] = {
    "os",
    "sys",
    "json",
    "typing",
    "pathlib",
    "datetime",
    "itertools",
    "functools",
    "collections",
    "subprocess",
    "math",
    "random",
    "re",
    "enum",
    "dataclasses",
}

DEV_DEPENDENCIES: List[str] = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "black>=24.0.0",
    "mypy>=1.0.0",
]


# ============================================================
# IMPORT EXTRACTION
# ============================================================


def extractImports(project_path: Path) -> Set[str]:
    """
    Extract top-level imports from Python files.

    :param project_path: Path = Source directory
    :return: Set[str] = Imported modules
    """
    imports: Set[str] = set()

    for file in project_path.rglob("*.py"):
        try:
            tree = ast.parse(file.read_text(encoding="utf-8"))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports.add(n.name.split(".")[0])

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])

        except Exception:
            continue

    return imports


# ============================================================
# DEPENDENCY MAPPING
# ============================================================


def mapToInstalledPackages(imports: Set[str]) -> List[str]:
    """
    Map imports to installed pip packages.

    :param imports: Set[str]
    :return: List[str]
    """
    installed = {
        dist.metadata["Name"].lower(): dist.version for dist in distributions()
    }

    dependencies: List[str] = []

    for imp in imports:
        key = imp.lower()

        # 🔥 ignora stdlib
        if key in STDLIB_MODULES:
            continue

        if key in installed:
            dependencies.append(f"{key}>={installed[key]}")

    return sorted(set(dependencies))


# ============================================================
# PYTHON VERSION
# ============================================================


def getPythonRequirement() -> str:
    major = sys.version_info.major
    minor = sys.version_info.minor

    return f">={major}.{minor},<{major}.{minor + 1}"


# ============================================================
# MAIN GENERATOR
# ============================================================


def generatePyproject(
    project_name: str,
    description: str,
    author: str,
    project_root: Path = Path("src"),
    home_page_git: str | None = None,
    repository_url: str | None = None,
) -> None:
    """
    Generate production-ready pyproject.toml with:
    - auto dependency detection
    - CI/CD ready config
    - automatic versioning via setuptools_scm

    :raises RuntimeError
    """
    try:
        imports = extractImports(project_root)
        dependencies = mapToInstalledPackages(imports)
        python_requirement = getPythonRequirement()

        pyproject_data = {
            # ============================================================
            # BUILD SYSTEM
            # ============================================================
            "build-system": {
                "requires": [
                    "setuptools>=65.0",
                    "wheel",
                    "setuptools_scm[toml]>=8.0",
                ],
                "build-backend": "setuptools.build_meta",
            },
            # ============================================================
            # PROJECT METADATA
            # ============================================================
            "project": {
                "name": project_name,
                "dynamic": ["version"],  # 🔥 REMOVE version fixa
                "description": description,
                "readme": "README.md",
                "requires-python": python_requirement,
                "authors": [{"name": author}],
                "dependencies": dependencies,
                "optional-dependencies": {
                    "dev": DEV_DEPENDENCIES
                    + [
                        "build",
                        "twine",
                    ]
                },
            },
            # ============================================================
            # TOOL CONFIGS
            # ============================================================
            "tool": {
                "setuptools": {"packages": {"find": {"where": ["src"]}}},
                # 🔥 VERSIONAMENTO AUTOMÁTICO
                "setuptools_scm": {
                    "version_scheme": "post-release",
                    "local_scheme": "no-local-version",
                },
                # 🔥 BLACK
                "black": {"line-length": 88},
                # 🔥 MYPY
                "mypy": {"strict": True},
                # 🔥 PYTEST
                "pytest": {"ini_options": {"testpaths": ["tests"]}},
            },
        }

        if repository_url:
            pyproject_data["project"]["urls"] = {
                "Homepage": home_page_git,
                "Repository": repository_url,
            }

        with open("pyproject.toml", "w", encoding="utf-8") as f:
            toml.dump(pyproject_data, f)

        print("pyproject.toml gerado com sucesso!")
        print(f"Runtime deps: {dependencies}")
        print(f"Dev deps: {DEV_DEPENDENCIES}")

    except Exception as exc:
        raise RuntimeError(f"Error generating pyproject.toml: {exc}") from exc


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    generatePyproject(
        project_name="pipefy",
        description="Secure and extensible credential management SDK for Python applications.",
        author="Rafael Cavalcante",
        home_page_git="https://github.com/rmcavalcante7/",
        repository_url="https://github.com/rmcavalcante7/infra-core-sdk",
    )
