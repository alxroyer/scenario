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


.. _coding-rules.py.inspection-warnings:

Inspection warnings
===================

In order to avoid non-relevant inspection warnings,
the ``# noqa`` pragma shall be used (after typehints if any).

In order to explicitize the reason why this pragma is used,
no code shall be given, just an explanatory comment after a double ``##`` with no final dot, as below:

.. code-block::

    def myfunction(
        type,  # type: typing.Any  # noqa  ## Shadows built-in name 'type'
    ):  # type: (...) -> typing.Any
        # ...

.. admonition:: No ``noqa`` codes
    :class: note

    ``noqa`` codes (like `E402` for "Module level import not at top of file" PEP8 warnings for instance)
    seem to be checker specific: `flake8`, IDEs, ...
    See https://www.alpharithms.com/noqa-python-501210/ for the history of this pragma.

    That's the reason why we choose to give no codes with ``# noqa`` pragmas.

.. admonition:: No final dot
    :class: note

    There are quite few reasons for the convention of not using final dots on ``# noqa`` explanations, but:

    - The explanation may be just a part of a warning taken from a tier tool, not a full sentence.
    - It makes the comment 1 character shorter, which may reduce the risk of having `too long lines` warnings.
    - Last but not least: many ``#noqa`` comments are already set without a final dot, so let's take it as the convention.
