.. Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..     http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.


.. _env:

Development environment
=======================

This section describes the tools constituting the development environment.


.. _env.tests:

Launch the tests
----------------

.. todo:: Documentation needed for testing:

    - ``./test/run-unit-campaign.py``
    - ``./test/run-unit-test.py``


.. _env.type-checking:

Type checking
-------------

.. todo:: Documentation needed for type checking:

    - ``./tools/check-types.py``
    - Adjust ``files`` and ``namespace_packages`` configurations in ``mypy.conf`` depending on mypy#9393 returns.

.. admonition:: ``tools/check-types.py`` integration in PyCharm

    - 'check-types.py' execution configurations:

      - Disbale "Add content roots to PYTHONPATH"
      - Disable "Add source roots to PYTHONPATH"
      - Disable "Run with Python Console"
      - Set Parameters with "--config-value scenario.log_date_time 0"

    - Execution:

      - First execution: Right-click on 'tools/check-types.py' > Run 'check-types'
      - Re-run: CTRL+F5

    - In the console, click on errors to directly get to the location of errors.


.. _env.encodings-and-perms:

Check encodings and file permissions
------------------------------------

.. todo:: Documentation needed for encoding checking:

    - ``repo-checkfiles``


.. _env.license-headers:

Check license headers
---------------------

.. todo:: Documentation needed for license headers:

    - ``repo-checklicense``


.. _env.build-doc:

Build documentation
-------------------

.. todo:: Documentation needed for building the documentation:

    - ``./tools/mkdoc.py``
