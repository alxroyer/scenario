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


.. _purpose:

Purpose of the `scenario` testing framework
===========================================

The `scenario` library is a framework for writing and executing full campaigns of tests,
with human-readable documentation.

A `scenario` test case is a sequence of `steps`, executed one after the others,
defining a `story` by the way.

---

One of the main interests of `scenario` is its ability to `reuse test code`:

- :ref:`Step objects <step-objects>`:
  Instanciate steps  one after the others, just like bricks,
  and quickly write different versions of a story
  (like a nominal test scenario, then alternative scenarios).
- :ref:`Subscenarios <subscenarios>`:
  Reuse existing test cases as subscenario utils,
  a fair way to set up initial conditions for instance.

Another strength of the `scenario` framework is its `documentation facilities`:

- Tie the test documentation (actions, expected results) right next to the related test code
  (see :ref:`quickstart <quickstart.first-scenario>` for an overview).
  By the way, the code is more understandable, and the whole easier to maintain.
- Easily collect test :ref:`evidence <evidence>`, just by using the :ref:`assertion API <assertions>` provided.
- Use :ref:`execution reports <reports>` to generate deliverable documentation in the end.

---

`scenario` also comes with a set of high quality features,
making tests easier to write and maintain:

- Rich :ref:`assertion API <assertions>`, with :ref:`evidence <evidence>` collection (as introduced above).
- Powerful :ref:`logging system <logging>`, with class loggers, indentation and colorization.
- Handful :ref:`configuration facilities <config-db>`.
- :ref:`Campaign <campaigns>` definition and execution.
- :ref:`Scenario <reports>` and :ref:`campaign reports <campaigns.reports>`.
- :ref:`Stability <stability>` investigation tools.
- Flexible :ref:`known issue <known-issues>` and test workaround tracking.
- ...
