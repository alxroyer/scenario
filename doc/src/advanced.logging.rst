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


.. _logging:

Logging
=======

Logging is one of the first useful means that help investigating on test executions.
That's the reason why a particular attention is paid to providing efficient logging facilities.

For the purpose, the :py:mod:`scenario` framework makes use and extends the standard :py:mod:`logging` library.


.. _logging.log-levels:

Log levels
----------

As :py:mod:`logging` proposes it, log levels are defined by ``int`` values.
The *ERROR*, *WARNING*, *INFO* and *DEBUG* log levels are mostly to be considered.

*ERROR*, *WARNING* and *INFO* log records are always displayed.
*DEBUG* log records may be displayed or not, depending on the context
(see :ref:`main logger <logging.main-logger>` and :ref:`class loggers <logging.class-loggers>` below).

Log levels are displayed within the log lines (usually after the :ref:`date/time <logging.date-time>`).
They are also commonly emphased with :ref:`colors <logging.colors.log-levels>` in the console, in order to facilitate hot analyses.


.. _logging.date-time:

Date / time
-----------

When analyzing test logs, the timing question is usually essential.

Log date/time is displayed by default at the beginning of the log lines,
with a ISO8601 pattern: ``YYYY-MM-DDTHH:MM:SS.mmmuuu+HH:MM``.

It may disabled through the :ref:`scenario.log_date_time <config-db.scenario.log_date_time>` configuration value.


.. _logging.main-logger:

Main logger
-----------

The :py:mod:`scenario` framework defines a main logger.
It uses a regular :py:class:`logging.Logger` instance with 'scenario' for name [#logging-instance-attribute]_.

It is accessible through the :py:attr:`scenario.logging` variable.

Debugging is enabled by default with this main logger.

.. literalinclude:: ../../demo/loggingdemo.py
    :language: python
    :lines: 22-29

.. literalinclude:: ../data/loggingdemo.log
    :language: none
    :lines: 5-11

.. admonition:: Implementation details
    :class: note

    The main logger carries the :py:class:`logging.Handler` instances.
    It ownes up to two handlers:

    1. A first one for the console output, always set.
    2. A second one, optional, for file logging when applicable (see :ref:`file logging <logging.outfile>`).


.. _logging.class-loggers:

Class loggers
-------------

Class loggers make it possible to classify sets of log lines with a given subject: the *log class*.
The *log class* is displayed within the log lines, between square brackets,
and furthermore makes it possible to enable or disable debug log lines for it.

A :py:class:`scenario.logger.Logger` instance may be created directly.

.. code-block:: python

    _logger = scenario.Logger("My logger")

But a common pattern is to inherit from :py:class:`scenario.logger.Logger`,
either directly (see :ref:`test libraries <test-libs>`) or through an intermediate class.
A couple of :py:mod:`scenario` classes inherit from the :py:class:`scenario.logger.Logger` class,
among others:

- :py:class:`scenario.Scenario`,
- :py:class:`scenario.Step`.

.. Inheriting from `scenario.Scenario`.
.. literalinclude:: ../../demo/loggingdemo.py
    :language: python
    :lines: 12-13, 17-18

.. todo:: Example needed for inheriting :py:class:`scenario.Step`.

A :py:class:`scenario.Scenario` instance is a class logger with the path of the Python script defining it as its *log class*.

A :py:class:`scenario.Step` instance takes the fully qualified name of the class or method defining it for *log class*.

Debugging is enabled by default for such user-defined scenario and step instances:

.. Step `LoggingScenario.step020()` python implementation.
.. literalinclude:: ../../demo/loggingdemo.py
    :language: python
    :lines: 12, 30-38

.. Step `LoggingScenario.step020()` console output.
.. literalinclude:: ../data/loggingdemo.log
    :language: none
    :lines: 13-19

Otherwise, debugging is disabled by default for class loggers.

.. Scenario `LoggingScenario` with `class_logger` member instance creation,
   and `LoggingScenario.step020()` python implementation.
.. literalinclude:: ../../demo/loggingdemo.py
    :language: python
    :lines: 12, 16-19, 39-47

.. Step `LoggingScenario.step030()` console output.
.. literalinclude:: ../data/loggingdemo.log
    :language: none
    :lines: 21-26

Class logger debugging can be activated on-demand, either 1) programmatically, ...:

.. Programmatic debug enabling.
.. literalinclude:: ../../demo/loggingdemo.py
    :language: python
    :lines: 49-53

.. Related console output.
.. literalinclude:: ../data/loggingdemo.log
    :language: none
    :lines: 27-29

... 2) through the ``--debug-class`` command line option, ...:

.. code-block:: bash

    $ ./bin/run-test.py --debug-class "My logger" ./demo/loggingdemo.py

... or 3) through the :ref:`scenario.debug_classes <config-db.scenario.debug_classes>` configuration value.

---

.. admonition:: Acces to :py:class:`logging.Logger` instances
    :class: tip

    .. [#logging-instance-attribute]
        In case you need to manipulate :mod:`logging` instance directly,
        the :py:class:`logging.Logger` instances are available through the :py:attr:`scenario.logger.Logger.logging_instance` property.

        The :py:attr:`scenario.logger.Logger.logging_instance` property is available to both main logger and class loggers.


.. _logging.colors:

Colors
------

The :py:mod:`scenario` framework manages colorization in the console, which facilitates hot analyses of the log flow.

Log colors may be disabled through the :ref:`scenario.log_color <config-db.scenario.log_color>` configuration value.


.. _logging.colors.log-levels:

Log level colorization
^^^^^^^^^^^^^^^^^^^^^^

The basic usage of log colorization is to highlight log levels:

- *ERROR*: colored in red,
- *WARNING*: colored in yellow,
- *INFO*: colored in white,
- *DEBUG*: colored in grey.

These default colors may be overriden with the :ref:`scenario.log_%(level)_color <config-db.scenario.log_level_color>` configuration values.

The log message also takes the color of its log level by default.


.. _logging.colors.log-class:

Class logger colorization
^^^^^^^^^^^^^^^^^^^^^^^^^

Log colors may also be applied for every log line of a given *log class*,
which is particularly useful when different class loggers generate interleaved log lines:

.. Call to `scenario.Logger.setlogcolor()`.
.. literalinclude:: ../../demo/loggingdemo.py
    :language: python
    :lines: 20


.. _logging.indentation:

Indentation
-----------

Log indentation also contributes in facilitating log analyses.

The :py:mod:`scenario` provides several indentation mechanisms.


.. _logging.indentation.scenario-stack:

Scenario stack indentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

When :ref:`sub-scenarios <subscenarios>` are executed, lines of '|' characters highlight the nestings of scenario executions.

Example of output from the `commutativeadditions.py <../../demo/commutativeadditions.py>`_ sample test.

.. Sub-scenario output log example: 'commutativeadditions.py'.
.. literalinclude:: ../data/commutativeadditions.log
    :language: none
    :lines: 1-51

*(Output truncated...)*

If a sub-scenario executes another sub-scenario, the '|' indentation is doubled, and so on.


.. _logging.indentation.class-logger:

Class logger indentation
^^^^^^^^^^^^^^^^^^^^^^^^

Additional indentation may be useful when the test makes verifications in a recursive way.

It may be set using the following methods:

- :py:meth:`scenario.logger.Logger.pushindentation()`,
- :py:meth:`scenario.logger.Logger.popindentation()`,
- :py:meth:`scenario.logger.Logger.resetindentation()`.

When these calls are made on a class logger,
the logging lines of this class logger are indented the way below.

.. Step `LoggingScenario.step110()` python implementation.
.. literalinclude:: ../../demo/loggingdemo.py
    :language: python
    :lines: 55-74

.. Step `LoggingScenario.step110()` console output.
.. literalinclude:: ../data/loggingdemo.log
    :language: none
    :lines: 31-49

.. admonition:: Additional indentation pattern
    :class: tip

    The :py:meth:`scenario.logger.Logger.pushindentation()` and :py:meth:`scenario.logger.Logger.popindentation()` methods
    have a ``indentation`` parameter that lets you change the 4-space default pattern by what you need.

    When removing indentation, the indentation pattern passed on must be the same as the one added in regards.

    .. code-block:: python

        self.class_logger.pushindentation("1> ")
        self.class_logger.pushindentation("2> ")
        self.class_logger.pushindentation("3> ")
        self.class_logger.popindentation("3> ")
        self.class_logger.popindentation("2> ")
        self.class_logger.popindentation("1> ")


.. _logging.indentation.main-logger:

Main logger indentation
^^^^^^^^^^^^^^^^^^^^^^^

When :py:meth:`scenario.logger.Logger.pushindentation()`, :py:meth:`scenario.logger.Logger.popindentation()`
and :py:meth:`scenario.logger.Logger.resetindentation()` calls are made on the main logger,
it takes effect on every log lines:

- main logger and class logger loggings (from *DEBUG* to *ERROR* log levels),
- but also actions, expected results and evidence texts.

.. Step `LoggingScenario.step120()` python implementation.
.. literalinclude:: ../../demo/loggingdemo.py
    :language: python
    :lines: 76-95

.. Step `LoggingScenario.step120()` console output.
.. literalinclude:: ../data/loggingdemo.log
    :language: none
    :lines: 51-69

.. admonition:: Scenario stack v/s user identation
    :class: note

    Even though main logger indentation applies to every log lines,
    it does not break the :ref:`scenario stack indentation <logging.indentation.scenario-stack>` presentation:
    the '|' characters remain aligned,
    the main logger indentation applies after.


.. _logging.debug:

Debugging
---------

Depending on the :ref:`logger configuration <logging.class-loggers>`, debug lines may be discarded.
By the way, formatting the whole logging message prior to discarding is a waste of time.
Depending on the amount of debugging information generated along the code, this can slow down the tests in a sensible way.

Such useless formatting processing can be saved by:

1. passing :ref:`format arguments as positional arguments <logging.debug.format-args>`,
2. :ref:`delaying string building <logging.debug.delayed-str>`.


.. _logging.debug.format-args:

Formatting & positional arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When logging a debug line, one can write:

.. code-block:: python

    self.debug("Hello I'm %s." % name)  # Option 1: `%` operator.
    self.debug(f"Hello I'm {name}")     # Option 2: f-string.
    self.debug("Hello I'm %s.", name)   # Option 3. positional arguments.

The second option is preferrable to the first one in as much as as
it is easier to maintain (main point for f-strings),
and f-strings are around 10% more efficient.

Still, with f-strings, the resulting string is computed before it is passed to the :py:meth:`scenario.logger.Logger.debug()` method,
and possibly discarded after being computed.

That's the reason why, the third option is even more efficient for debug logging:
a useless message will be discarded before the formatting arguments are applied to it.


.. _logging.debug.delayed-str:

Delayed strings
^^^^^^^^^^^^^^^

Even when passing format arguments as positionals,
some of them may take a while being computed by themselves.

That's the reason why the :py:mod:`scenario.debug` package gathers a couple of functions and classes that enable delaying more string computations:

.. list-table::
    :widths: auto
    :header-rows: 1
    :stub-columns: 0

    * - Function
      - Class
      - Description
      - Example

    * -
      - :py:class:`scenario.debugutils.DelayedStr`
      - Abstract class that defines a string which computation may be delayed.

        You may inherit from this base class for specific needs.
      -

    * -
      - :py:class:`scenario.debugutils.FmtAndArgs`
      - Describes a delayed string that should be built with format and arguments.

        The string can be prepared step by step, thanks to the :py:meth:`scenario.debugutils.FmtAndArgs.push()` method.

        The application of the arguments is delayed on time when needed.
      - .. code-block:: python

            _str = scenario.debug.FmtAndArgs("Hello, I'm %s", name)
            if profession:
                _str.push(" and I'm a %s", profession)
            _str.push(".")
            self.debug(_str)

    * - :py:func:`scenario.debugutils.saferepr()`
      - :py:class:`scenario.debugutils.SafeRepr`
      - Computes a *repr*-like string, but ensures a *not-too-long* string, possibly focused on certain parts,
        such computation being delayed as for the others.
      - .. code-block:: python

            self.debug(
                "%s in %s",
                scenario.debug.saferepr(searched),
                scenario.debug.saferepr(longtext, focus=searched),
            )

    * - :py:func:`scenario.debugutils.jsondump()`
      - :py:class:`scenario.debugutils.JsonDump`
      - Delays the dump computation for JSON data.
      - .. code-block:: python

            self.debug(
                "JSON data: %s", scenario.debug.jsondump(data, indent=2),
                extra=self.longtext(max_lines=10),
            )

        .. tip:: :py:func:`scenario.debugutils.jsondump()` may basically be displayed as :ref:`long texts <logging.long-text>`.

    * - :py:func:`scenario.debugutils.callback()`
      - :py:class:`scenario.debugutils.CallbackStr`
      - Delays the execution of a string builder callback.

        Possibly set with a lambda, this function makes it possible to delay quite everything.
      - .. code-block:: python

            self.debug(
                "Very special data: %s",
                scenario.debug.callback(lambda x, y, z: ..., arg1, arg2, arg3),
            )


.. _logging.long-text:

Long texts
^^^^^^^^^^

The :py:mod:`scenario` logging feature provides a way to log long texts on several lines.

To do so, set the ``extra`` parameter using the :py:meth:`scenario.logger.Logger.longtext()` method when logging some text:

.. code-block:: python

    self.debug(scenario.jsondump(_json_data, indent=2),
               extra=self.longtext(max_lines=10))

This feature has primarily been designed for debugging, but it works with the
:py:meth:`scenario.logger.Logger.info()`,
:py:meth:`scenario.logger.Logger.warning()` and
:py:meth:`scenario.logger.Logger.error()`
methods as well.

The ``max_lines`` parameter may be set to ``None`` in order to display the full text.


.. _logging.outfile:

File logging
------------

The :py:mod:`scenario` logging feature provides the ability to save the test log output into a file.

To do so, set the :ref:`scenario.log_file <config-db.scenario.log_file>` configuration value,
either with the ``–-config-value`` command line option, or within a configuration file.

The command line example below
disables the output in the console,
but saves it into the 'doc/data/commutativeaddition.log' file
(from the main directory of the :py:mod:`scenario` library):

.. code-block:: bash

    $ mkdir -p ./doc/data
    $ ./bin/run-test.py \
        --config-value "scenario.log_console" "0" \
        --config-value "scenario.log_file" "./doc/data/commutativeaddition.log" \
        ./demo/commutativeaddition.py
    $ cat ./doc/data/commutativeaddition.log

.. literalinclude:: ../data/commutativeaddition.log
    :language: none

.. tip::

    The :ref:`scenario.log_file <config-db.scenario.log_file>` configuration value may also be set programmatically
    through the :py:meth:`scenario.configdb.ConfigDatabase.set()` method,
    as illustrated in the :ref:`launcher script extension <launcher.pre-post>` section.


.. _logging.extra-flags:

Extra flags
-----------

The :py:class:`scenario.logextradata.LogExtraData` define a set of flags that can be set to specialize the behaviour of each :py:class:`scenario.logger.Logger`.

For instance, the :py:class:`scenario.scenariorunner.ScenarioRunner` and :py:class:`scenario.scenariostack.ScenarioStack` classes
disable the :py:const:`scenario.logextradata.LogExtraData.ACTION_RESULT_MARGIN` flag,
so that their related log lines remain aligned on the left whatever the current action / expected result context is.

Please, refer the following links for details on extra flags:

- :py:class:`scenario.logextradata.LogExtraData`
- :py:meth:`scenario.logger.Logger.setextraflag()`

.. warning::
    Setting extra flags on class loggers, or even worse on the main logger, may lead to unpredictable behaviours.

    Nevertheless, this advanced feature is provided as is.
    To be used with parsimony.
