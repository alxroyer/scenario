.. Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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


.. _purpose:

Purpose of the `scenario` framework
===================================

:py:mod:`scenario` is a framework to write and execute full campaigns of functional tests.

A scenario test case is a set of ordered steps executed one after the others.
It describes a story from the beginning to the end of the test.

One of the main interets of working with :py:mod:`scenario` is its ability to reuse a scenario, either:

- to derivate the normal set of steps of a nominal scenario in order to write error test cases from the first one,
- or in initial condition steps, to bring the software or system under test in an appropriate state before the actual test steps begin.

The :py:mod:`scenario` framework also comes with a set of useful features to write, execute and debug tests:

- :ref:`log classes <logging.class-loggers>`, logging :ref:`indentation <logging.indentation>` and :ref:`colorization <logging.colors>`,
- :ref:`rich assertions <assertions>`,
- :ref:`evidence collection <evidence>`,
- :ref:`configurations <config-db>`,
- :ref:`handlers <handlers>`,
- :ref:`campaign executions <campaigns>`,
- :ref:`scenario <reports>` and :ref:`campaign report <campaigns.reports>` generations,
- ...
