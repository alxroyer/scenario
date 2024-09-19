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


.. _config-db:

Configuration database
======================

The `scenario` framework provides a general configuration database.

It is available through the :py:data:`scenario.conf` attribute.


Configuration nodes
-------------------

The database configuration is a tree of sections, sub-sections, sub-sub-sections, ... ending with final values.

The :py:class:`scenario._confignode.ConfigNode` class describes a node in the resulting configuration tree,
either a section or a final value.


Configuration tree & keys
-------------------------

Configuration keys are a simplified form of `JSONPath <https://tools.ietf.org/id/draft-goessner-dispatch-jsonpath-00.html>`_:
they are dot-separated strings, with the ability to index a single list item with a number between square brackets.

With the following sample data:

.. literalinclude:: ../../../demo/conf.yml
    :language: yaml

- `"a.b.c"` points to the 55 value,
- `"x.y[2].z"` points to the 102 value,
- `"a.b"` points to the so-named sub-section (the corresponding data being a ``dict``),
- `"x.y"` points to the so-named list (the corresponding data being a ``list``),
- `""` (empty string) points to root node.

.. tip:: Configuration keys may be passed as strings or string enums.


Loading and setting configurations through the command line
-----------------------------------------------------------

Configuration values are basically set through the command line,
with the ``--config-file`` and/or ``--config-value`` options of test and campaign launchers.

.. literalinclude:: ../../data/run-test.help.log
    :language: none

Configuration files can be in one of the following formats:

.. list-table:: Configuration file formats
    :widths: auto
    :header-rows: 1
    :stub-columns: 0

    * - Format
      - File extensions
    * - INI (as handled by `configparser <https://docs.python.org/3/library/configparser.html>`_)
      - *.ini*, *.INI*
    * - JSON
      - *.json*, *.JSON*
    * - YAML (requires `PyYAML <https://pypi.org/project/PyYAML/>`_ to be installed)
      - *.yaml*, *.yml*,
        *.YAML*, *.YML*

Several files may be loaded consecutively by repeating the ``--config-file`` option.

This makes it possible to split configuration files on various purposes:

- the kind of software / system under test,
- the environment used to execute the tests,
- the identity of the person who launches the tests,
- ...

The configuration data from the different files is merged all together in the resulting tree,
the values set from the latter files overloading the ones already set by the formers files.

Then, the single values set by the ``--config-value`` options finally update the configuration tree.

.. admonition:: Boolean value conversions
    :class: tip

    When configuration values are boolean values,
    they may be passed as strings in one of the usual forms recognized:

    :*True* values: any non-zero integer or integer string, strings like "True", "TRUE", "true", "Yes, "YES", "yes", "Y", "y"
    :*False* values: 0 (zero) or "0", strings like "False", "FALSE", "false", "No", "NO", "no", "N", "n"


Manipulating configurations from the code
-----------------------------------------

The code can then access configuration values (resp. :py:class:`scenario._confignode.ConfigNode` instances)
through the :py:meth:`scenario._configdb.ConfigDatabase.get()` method (resp. :py:meth:`scenario._configdb.ConfigDatabase.getnode()`).

.. code-block:: python

    # Access a final value (`None` if the value does not exist).
    _any = scenario.conf.get("a.b.c")  # type: typing.Optional[typing.Any]
    # Access a final value of the given type (`None` if the value does not exist).
    _int1 = scenario.conf.get("a.b.c", type=int)  # type: typing.Optional[int]
    # Access a final value, or fallback to a default value.
    _int2 = scenario.conf.get("a.b.c", type=int, default=100)  # type: int
    # Access a whole section as a JSON dictionary (`None` if the section does not exist).
    _section = scenario.conf.get("a", type=dict)  # type: typing.Optional[typing.Dict[str, typing.Any]]
    # Access a whole list as a JSON list (`None` if the list does not exist).
    _list = scenario.conf.get("x.y", type=list)  # type: typing.Optional[typing.List[typing.Any]]

The configuration keys available can be listed with the :py:meth:`scenario._configdb.ConfigDatabase.getkeys()` method.

Configuration files can be loaded from the code (see :py:meth:`scenario._configdb.ConfigDatabase.loadfile()`).

.. code-block:: python

    # Load a configuration file.
    scenario.conf.loadfile("demo/conf.yml")

Configuration data can also be set (either sections or lists or single values, see :py:meth:`scenario._configdb.ConfigDatabase.set()`).

.. code-block:: python

    # Set a single value.
    scenario.conf.set("a.b.c", 150)
    # Update a whole section (possibly with sub-sections).
    scenario.conf.set("a.b", {"c": 200})
    scenario.conf.set("a", {"b": {"c": 200}})

.. admonition:: Automatic configuration data conversions
    :class: tip

    When setting data from the code, the configuration database applies the following conversions:

    .. list-table:: Automatic configuration data conversions
        :widths: auto
        :header-rows: 1
        :stub-columns: 0

        * - Input data type
          - Storage
        * - Path-likes
          - ``str`` form of the path, using ``os.fspath()``
        * - ``enum.EnumMeta``
          - ``list``
        * - ``enum.IntEnum``
          - ``int`` form of the enum value
        * - Other ``enum.Enum``
          - ``str`` form of the enum value

Configuration nodes can be accessed directly from the code, and provide an API that can be used from the user code
(see :py:class:`scenario._confignode.ConfigNode`).

.. code-block:: python

    # Access a configuration node (`None` if the node does not exist).
    _node = scenario.conf.getnode("a.b.c")  # type: typing.Optional[scenario.ConfigNode]


Configuration origins
---------------------

In case configurations lead to some erroneous situation,
the configuration database keeps memory of *configuration origins*
(see :py:attr:`scenario._confignode.ConfigNode.origins` and :py:attr:`scenario._confignode.ConfigNode.origin`).

This information can help a user fix his/her configuration files when something goes wrong.

For the purpose, the :py:meth:`scenario._confignode.ConfigNode.errmsg()` method
builds error messages giving the representative origin of the given configuration node.

The :py:meth:`scenario._configdb.ConfigDatabase.show()` and :meth:`scenario._confignode.ConfigNode.show()` methods
also display the configuration tree with origins.

.. code-block:: bash

    $ ./demo/run-demo.py --config-file demo/conf.json --config-value x.y[0].z 0 --show-configs demo/htmllogin.py

.. Skip the 'scenario' section.
.. literalinclude:: ../../data/run-demo.show-configs.log
    :lines: -4, 8-


.. _config-db.scenario:

`scenario` configurable keys and values
---------------------------------------

.. include:: config-db-scenario.rst
