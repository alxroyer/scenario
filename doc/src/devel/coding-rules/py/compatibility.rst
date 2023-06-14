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


.. _coding-rules.py.compatibility:

Python compatibility
====================

The code supports Python versions from 3.6.

The 'tools/check-types.py' scripts checks code amongst Python 3.6.

.. admonition:: Python versions
    :class: note

    No need to handle Python 2 anymore, as long as its end-of-line was set on 2020-01-01
    (see `PEP 373 <https://www.python.org/dev/peps/pep-0373/>`_).

    As of 2021/09, Python 3.6's end-of-life has not been declared yet (see `<https://devguide.python.org/devcycle/#end-of-life-branches>`_),
    while Python 3.5's end-of-life was set on 2020-09-30 (see `PEP 478 <https://www.python.org/dev/peps/pep-0478/>`_).
