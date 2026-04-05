from __future__ import annotations

import os
import sys
from datetime import datetime, UTC


ROOT = os.path.abspath("..")
SRC = os.path.abspath("../src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)


project = "PipeBridge"
author = "Rafael Mota Cavalcante"
copyright = f"{datetime.now(UTC).year}, {author}"
language = "en"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

html_theme = "furo"
html_title = "PipeBridge"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "source_repository": "https://github.com/rmcavalcante7/pipebridge/",
    "source_branch": "main",
    "source_directory": "docs/",
    "top_of_page_button": "edit",
    "footer_icons": [],
}

