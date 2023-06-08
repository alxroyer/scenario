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


.. _coding-rules.py.static:

Static & class methods
======================

Do not use the ``@staticmethod`` or ``@classmethod`` decorator whenever a method could be converted so.
It is preferrable to rely on the meaning at first, in order to make the code more stable along the time.

By default, Python IDEs may detect any methods which could safely be made static.
Such inspection warnings go against the statement above.
Please disable such inspection rule in your IDE settings if any.

.. admonition:: PyCharm inspection configuration
    :class: tip

    As of PyCharm 2021.2, uncheck the following option:
    "File" > "Settings" > "Editor" > "Inspections" > (select profile) > "Python" > "Method is not declared static".
