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


.. _coding-rules.documentation.domains:

Domains
=======

.. admonition:: Default domain
    :class: note

    Unless the ``.. default-domain::`` directive is used,
    the `Python domain <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#the-python-domain>`_
    is the `default domain <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#basic-markup>`_.

We do not use the ``:py`` domain specification in the Python docstrings, in as much as it is implicit.

However, we use the ``:py`` domain specification in `.rst` files in order to be explicit for `cross referencing python objects
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#cross-referencing-python-objects>`_.
