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


.. _launcher:

Launcher script extension
=========================

It is common that a user test environment needs to do a couple of things like:

- prepare the environment before the test execution,
- execute additional actions after the test execution,
- offer configurable features.

To do so, the user test environment may define its own launcher script,
as illustrated by the `demo/run-demo.py <https://github.com/alxroyer/scenario/blob/master/demo/run-demo.py>`_ file.


.. _launcher.extend-args:

Command line argument extension
-------------------------------

About configurable features, :ref:`configuration files <config-db>` come as a straight forward solution.
Nevertheless, it is sometimes faster in use to provide command line options to the test launcher script also.
To do so, our 'demo/run-demo.py' first overloads the :py:class:`scenario._scenarioargs.ScenarioArgs` class:

- The final program description is set with the :py:meth:`scenario._args.Args.setdescription()` method.
- Extra arguments may be defined thanks to the :py:meth:`scenario._args.Args.addarg()` then :py:meth:`scenario._args.ArgInfo.define()` methods.

.. Class declaration with constructor.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: class DemoArgs
    :end-before: def _checkargs

The :py:meth:`scenario._args.Args._checkargs()` method may be overloaded in order to check additional constraints,
after the arguments have been parsed, and the :py:class:`scenario._args.Args` attributes have been updated:

- Start or finish with calling the mother class's :py:meth:`scenario._scenarioargs.ScenarioArgs._checkargs()` method.
- This method is expected to return ``True`` or ``False`` whether an error has been detected or not.

.. Overload of the `_checkargs()` method.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: def _checkargs
    :end-at: return True

Then, in the *main* part, prior to calling the :py:meth:`scenario._scenariorunner.ScenarioRunner.main()` method:

- Set an instance of our :py:class:`DemoArgs` class with the :py:meth:`scenario._args.Args.setinstance()` method.
- Call the :py:meth:`scenario._args.Args.parse()` method to parse the command line arguments.

.. Argument parsing.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # Command line arguments.
    :end-at: sys.exit
    :dedent:

At this point, the user test environment can use the extra arguments added with the :py:class:`DemoArgs` class,
but regular arguments as well.

.. Use of arguments.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # --show-configs option.
    :end-at: Test log saved
    :dedent:

Using the ``--help`` option displays both:

- the usual :py:class:`scenario._scenarioargs.ScenarioArgs` options,
- and the extra options added by the :py:class:`DemoArgs` class.

.. code-block:: bash

    $ ./demo/run-demo.py --help

.. literalinclude:: ../../data/run-demo.help.log
    :language: none


.. _launcher.pre-post:

Pre & post-operations
---------------------

As introduced above, extending the launcher script gives you the opportunity to add
pre-operations, as soon as the command line arguments have been parsed,
and post-operations after the test execution.

Our `demo/run-demo.py <https://github.com/alxroyer/scenario/blob/master/demo/run-demo.py>`_ script gives examples of pre & post-operations:

- a welcome message displayed before the test is executed:

.. Welcome message.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # Welcome message.
    :end-at: scenario.logging.info
    :dedent:

- a bye message displayed just before the command line ends:

.. Bye message.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # Bye message.
    :end-at: scenario.logging.info
    :dedent:

- optional display of the configuration database:

.. Configuration database display.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # --show-configs option.
    :end-at: sys.exit
    :dedent:

- :ref:`file logging <logging.outfile>` enabling:

.. File logging.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # File logging:
    :end-at: scenario.logging.info
    :dedent:

.. admonition:: Launchers and configuration database.
    :class: tip

    Please note the ability to configure the `scenario` framework behaviours
    with the help of the :ref:`configuration database <config-db.scenario>`.

- configuration of the :ref:`scenario attributes <scenario-attributes>` expected for each:

.. Expected scenario attributes.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # Configure the list of expected scenario attributes.
    :end-at: ])
    :dedent:


.. _launcher.execution:

Base launcher execution
-----------------------

The call to the :py:meth:`scenario._scenariorunner.ScenarioRunner.main()` method will not analyze command line arguments twice,
and use the values given by our :py:class:`DemoArgs` instance already set.

.. Scenario execution.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # Scenario execution.
    :end-at: scenario.runner.main()
    :dedent:


.. _launcher.ret-code:

Return code
-----------

Eventually, convert the enum value returned by :py:meth:`scenario._scenariorunner.ScenarioRunner.main()` into a simple integer value,
so that the error can be handled in the shell that launched the command line.

.. Error code.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # Error code.
    :end-at: sys.exit
    :dedent:


.. _launcher.campaigns:

Campaign launcher script extension
----------------------------------

Extending the campaign launcher script works the same, except that:

- the :py:class:`scenario._campaignargs.CampaignArgs` class may be overloaded to add extra command line arguments,
- the :py:meth:`scenario._campaignrunner.CampaignRunner.main()` must be called in the end.


.. _launcher.main-path:

Setting the main path (optional)
--------------------------------

Another thing that a launcher script may do is to set the *main path*
(see :py:meth:`scenario._path.Path.setmainpath()`).

A *main path* shall be set for the current test projet.
This way, all paths displayed during the tests may be nicely displayed as *pretty path* from this *main path*,
whatever the current working directory
(see :py:attr:`scenario._path.Path.prettypath`).

.. Setting the main path.
.. literalinclude:: ../../../demo/run-demo.py
    :language: python
    :start-at: # Main path.
    :end-at: scenario.Path.setmainpath
    :dedent:

.. tip::
    For display purpose, it is advised to set the *main path* after the program arguments have been analyzed.
