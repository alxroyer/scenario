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


.. _multiple-executions:

Multiple scenario executions
============================

As described by the scenario launcher help message,
several scenarios may be executed with a single command line.

.. literalinclude:: ../data/run-test.help.log
    :language: none

For example:

.. code-block:: bash

    $ ./bin/run-test.py demo/commutativeaddition.py demo/loggingdemo.py

.. admonition:: Option restriction
    :class: note

    When executing several scenarios in the same command line,
    a couple of options come to be not applicable,
    such as ``--json-report``.

The tests are executed one after the other, in the order given by the command line.

A summary of the scenario executions is given in the end.

.. literalinclude:: ../data/commutativeaddition+loggingdemo.summary.log
    :language: none
