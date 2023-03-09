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


.. _test-libs:

User test libraries
===================

.. todo:: Documentation needed for user test libraries.

    Create test libraries by inheriting both :py:class:`scenario.assertions.Assertions` and :py:class:`scenario.logger.Logger`.

    .. Inheriting from `scenario.Logger`.
    .. literalinclude:: ../../demo/loggingdemo.py
        :language: python
        :start-at: class MyLogger
        :end-at: scenario.Logger.__init__

    .. Inheriting from both `scenario.Assertions` and `scenario.Logger`.
    .. literalinclude:: ../../demo/htmltestlib.py

    Memo: Debugging is disabled by default for class loggers.
