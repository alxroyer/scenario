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


.. _coding-rules.py.strings:

Strings
=======

.. todo:: Documentation needed for string coding rules:

    - Differenciate strings and byte-strings:
        - Usage of ``""`` / ``r""`` / ``f""`` (double quote) to enclose ``str`` strings
            - Except for strings in f-string {}-blocks => simple quotes
            - Except for strings containing lots of ``"`` characters (HTML generation for instance)
            - Justification:
                - `Python Single vs. Double Quotes - Which Should You Use And Why? | Better Data Science <https://betterdatascience.com/python-single-vs-double-quotes/>`_
                - `PEP8: PEP 8 – Style Guide for Python Code | peps.python.org <https://peps.python.org/pep-0008/#string-quotes>`_
                - PEP8 gives no clear recommendation on the subject, which makes our choice compatible.
                - Other languages usually use ``"`` for strings, so this choice looks natural.
                - Better to have systematic presentation for uniformity, and avoid merge conflicts.
        - Usage of ``b''`` / ``rb''`` (simple quotes) to enclose ``bytes`` strings
    - Use f-strings
        - Except for debugging (for optimization concerns)
        - Except for assertion errors and evidence (for optimization concerns)
        - Except for regex (because of '{}' escaping)
        - Except for bytes (f-strings not available)
    - Use *repr* specification (``f"{...!r}"`` / ``"%r"``) instead of calling ``repr()`` (for optimization concerns)
