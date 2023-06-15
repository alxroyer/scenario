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


.. _campaigns:

Campaigns
=========

Campaigns shall be launched with the 'run-campaign.py' script.

.. literalinclude:: ../../data/run-campaign.help.log
    :language: none


.. _campaigns.test-suite-files:

Test suite files
----------------

Test suite files are text files that describe the scenario files to execute, or not to execute.

Example from the `demo.suite <https://github.com/alxroyer/scenario/blob/master/demo/demo.suite>`_ test suite file:

.. literalinclude:: ../../../demo/demo.suite
    :language: none

.. list-table:: Test suite files syntax
    :widths: auto
    :header-rows: 1
    :stub-columns: 0

    * - Type of line
      - Syntax
      - Effects
    * - Comment
      - Starts with a '#' character.
      - No effect.
    * - White list
      - Starts with a '+' character, or no starter character,
        followed by a path or a glob-style pattern.
      - Describes one (or several) script path(s) of scenario(s) to execute.

        When the path is relative, it is computed from the test suite file directory.
    * - Black list
      - Starts with a '-' character,
        followed by a path or a glob-style pattern.
      - Describes one (or several) script path(s) to remove from the white list constituted by the preceding lines.

        When the path is relative, it is computed from the test suite file directory.

.. tip:: White-list lines after a black-list line may restore script paths avoided by the latter.


.. _campaigns.execution:

Campaign execution
------------------

Test suite files are executed one after the others, in the order given by the command line.

A summary of the tests executed is displayed in the end.

.. code-block:: bash

    $ ./bin/run-campaign.py demo/demo.suite

.. literalinclude:: ../../data/demo.campaign.log
    :language: none


.. _campaigns.reports:

Campaign reports
----------------

The ``--outdir`` option specifies the directory where the execution reports should be stored.

.. admonition:: ``--dt-subdir`` option
    :class: tip

    In conjonction with it, the ``--dt-subdir`` option tells the 'run-campaign.py' launcher to create a date/time subdirectory in the output directory.

    The date/time subdirectory is formed on the 'YYYY-MM-DD_HH-MM-SS' pattern.

For each scenario executed, a :ref:`JSON report <reports>` is stored in the output directory.

Eventually, a campaign report is generated in the XML JUnit format.

.. literalinclude:: ../../data/demo.campaign.xml
    :language: xml

.. admonition:: XML JUnit format
    :class: note

    A reference documentation could not be found for the XML JUnit format.

    In spite of, the `[CUBIC] <https://llg.cubic.org/docs/junit/>`_ page can be noted as one of the best resources on that topic.
