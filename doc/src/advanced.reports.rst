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


.. _reports:

Reports
=======

Reports may be generated when executing a single scenario, with the ``--json-report`` option:

.. code-block:: bash

    $ ./bin/run-test.py ./demo/commutativeaddition.py --json-report ./demo/commutativeaddition.json

Below, the JSON output file for the :ref:`quickstart <quickstart.first-scenario>` ``CommutativeAddition`` sample scenario:

.. literalinclude:: ../data/commutativeaddition.json
    :language: javascript

.. note:: Dates are ISO-8601 encoded, and elapsed times are given in seconds.
          They are figured with the respective patterns 'YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM' and 'SSS.mmmmmm' above.

.. todo:: Documentation needed for campaign reports
