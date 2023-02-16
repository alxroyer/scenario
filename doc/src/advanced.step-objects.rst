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


.. _step-objects:

Step objects: instanciate steps and sequence them as scenarios
==============================================================

The :ref:`quickstart <quickstart>` showed how to quickly write a first test scenario using ``step...()`` methods.

However, test code reuse can hardly be achieved with step methods.
In order to be able to reuse steps between different scenarios,
it is better defining them as classes, inheriting from :py:class:`scenario.Step`.


.. todo:: Documentation needed for steps as objects.


.. _step-objects.alternative-scenarios:

Alternative scenarios
---------------------

.. todo:: Documentation needed for alternative scenarios.
