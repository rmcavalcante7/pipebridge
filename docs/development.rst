Development
===========

Local Setup
-----------

.. code-block:: bash

   pip install -e .[dev]

Quality Gates
-------------

The project is configured to block on:

- ``black --check .``
- ``mypy src``
- ``pytest tests/unit tests/functional``

Run them locally with:

.. code-block:: bash

   python -m black --check .
   python -m mypy src
   python -m pytest tests/unit tests/functional -v

Integration Tests
-----------------

Integration tests use the real Pipefy API and require:

- ``PIPEFY_API_TOKEN``
- ``PIPEFY_BASE_URL`` optional

.. code-block:: powershell

   $env:PIPEFY_API_TOKEN="YOUR_TOKEN"
   $env:PIPEFY_BASE_URL="https://app.pipefy.com/queries"
   python -m pytest tests/integration -v

Build Local HTML Docs
---------------------

.. code-block:: bash

   pip install -e .[docs]
   sphinx-build -b html docs docs/_build/html
