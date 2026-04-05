Quick Start
===========

Installation
------------

.. code-block:: bash

   pip install pipebridge

Facade Entry Point
------------------

.. code-block:: python

   from pipebridge import PipeBridge

   api = PipeBridge(
       token="YOUR_TOKEN",
       base_url="https://app.pipefy.com/queries",
   )

   card = api.cards.get("123456789")
   print(card.title)

Main Public Domains
-------------------

- ``api.cards``
- ``api.phases``
- ``api.pipes``
- ``api.files``

Safe Card Update
----------------

.. code-block:: python

   from pipebridge import CardUpdateConfig

   result = api.cards.updateFields(
       card_id="123",
       fields={
           "title": "New value",
           "priority": "High",
       },
       expected_phase_id="456",
       config=CardUpdateConfig(
           validate_field_existence=True,
           validate_field_options=True,
           validate_field_type=True,
           validate_field_format=True,
       ),
   )

Safe Card Move
--------------

.. code-block:: python

   from pipebridge import CardMoveConfig

   result = api.cards.moveSafely(
       card_id="123",
       destination_phase_id="999",
       expected_current_phase_id="456",
       config=CardMoveConfig(validate_required_fields=True),
   )

File Upload
-----------

.. code-block:: python

   from pipebridge import FileUploadRequest

   request = FileUploadRequest(
       file_name="sample.txt",
       file_bytes=b"content",
       card_id="123",
       field_id="attachments",
       organization_id="999",
   )

   result = api.files.uploadFile(request)
