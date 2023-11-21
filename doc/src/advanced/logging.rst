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


.. _logging:

Logging
=======

Logging is one of the first useful means that help investigating on test executions.
That's the reason why a particular attention is paid to providing efficient logging facilities.

For the purpose, the `scenario` framework makes use and extends the standard ``logging`` library.


.. _logging.log-levels:

Log levels
----------

As the system ``logging`` module proposes it, log levels are defined by ``int`` values.
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

It may be disabled through the :ref:`scenario.log_datetime <config-db.scenario.log_datetime>` configuration value.


.. _logging.main-logger:

Main logger
-----------

The `scenario` framework defines a main logger.
It uses a regular ``logging.Logger`` instance with ``'scenario'`` for name [#logging-instance-attribute]_.

It is accessible through the :py:data:`scenario.logging` variable.

Debugging is enabled by default with this main logger.

.. literalinclude:: ../../../demo/loggingdemo.py
    :language: python
    :start-at: def step010
    :end-at: This is debug.

.. literalinclude:: ../../data/loggingdemo.log
    :language: none
    :start-at: STEP#1:
    :end-at: This is debug.

.. admonition:: Implementation details
    :class: note

    The main logger carries the ``logging.Handler`` instances.
    It ownes up to two handlers:

    1. A first one for the console output, always set.
    2. A second one, optional, for file logging when applicable (see :ref:`file logging <logging.outfile>`).


.. _logging.class-loggers:

Class loggers
-------------

Class loggers make it possible to classify sets of log lines with a given subject: the *log class*.
The *log class* is displayed within the log lines, between square brackets,
and furthermore makes it possible to enable or disable debug log lines for it.

A :py:class:`scenario._logger.Logger` instance may be created directly.

.. code-block:: python

    _logger = scenario.Logger("My logger")

But a common pattern is to inherit from :py:class:`scenario._logger.Logger`,
either directly (see :ref:`test libraries <test-libs>`) or through an intermediate class.
A couple of `scenario` classes inherit from the :py:class:`scenario._logger.Logger` class,
among others:

- :py:class:`scenario.Scenario`,
- :py:class:`scenario.Step`.

.. Inheriting from `scenario.Scenario`.
.. literalinclude:: ../../../demo/loggingdemo.py
    :language: python
    :start-at: class LoggingScenario
    :end-at: scenario.Scenario.__init__

.. todo:: Example needed for inheriting :py:class:`scenario.Step`.

A :py:class:`scenario.Scenario` instance is a class logger with the path of the Python script defining it as its *log class*.

A :py:class:`scenario.Step` instance takes the fully qualified name of the class or method defining it for *log class*.

Debugging is enabled by default for such user-defined scenario and step instances:

.. Step `LoggingScenario.step020()` python implementation.
.. literalinclude:: ../../../demo/loggingdemo.py
    :language: python
    :start-at: def step020(self):
    :end-at: self.debug("This is debug.")
    :dedent:

.. Step `LoggingScenario.step020()` console output.
.. literalinclude:: ../../data/loggingdemo.log
    :language: none
    :start-at: STEP#2:
    :end-before: This is debug.

Otherwise, debugging is disabled by default for class loggers.

.. Scenario `LoggingScenario` with `class_logger` member instance creation.
.. literalinclude:: ../../../demo/loggingdemo.py
    :language: python
    :start-at: self.class_logger = MyLogger()
    :end-at: self.class_logger.setlogcolor(scenario.Console.Color.LIGHTBLUE36)
    :dedent:

.. Step `LoggingScenario.step030()` python implementation.
.. literalinclude:: ../../../demo/loggingdemo.py
    :language: python
    :start-at: def step030(self):
    :end-before: Activate debugging for the class logger instance.
    :dedent:

.. Step `LoggingScenario.step030()` console output.
.. literalinclude:: ../../data/loggingdemo.log
    :language: none
    :start-at: STEP#3:
    :end-before: Activate debugging for the class logger instance.

Class logger debugging can be activated on-demand, either 1) programmatically, ...:

.. Programmatic debug enabling.
.. literalinclude:: ../../../demo/loggingdemo.py
    :language: python
    :start-at: Activate debugging for the class logger instance.
    :end-at: This is debug again.
    :dedent:

.. Related console output.
.. literalinclude:: ../../data/loggingdemo.log
    :language: none
    :start-at: Activate debugging for the class logger instance.
    :end-at: This is debug again.

... 2) through the ``--debug-class`` command line option, ...:

.. code-block:: bash

    $ ./bin/run-test.py --debug-class "My logger" ./demo/loggingdemo.py

... or 3) through the :ref:`scenario.debug_classes <config-db.scenario.debug_classes>` configuration value.

---

.. admonition:: Access to ``logging.Logger`` instances
    :class: tip

    .. [#logging-instance-attribute]

        In case you need to manipulate ``logging`` instances directly,
        the ``logging.Logger`` instances are available through the :py:attr:`scenario._logger.Logger.logging_instance` property.

        The :py:attr:`scenario._logger.Logger.logging_instance` property is available to both main logger and class loggers.


.. _logging.colors:

Colors
------

The `scenario` framework manages colorization in the console, which facilitates hot analyses of the log flow.

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
.. literalinclude:: ../../../demo/loggingdemo.py
    :language: python
    :start-at: setlogcolor
    :lines: 1
    :dedent:


.. _logging.indentation:

Indentation
-----------

Log indentation also contributes in facilitating log analyses.

The `scenario` framework provides several indentation mechanisms.


.. _logging.indentation.scenario-stack:

Scenario stack indentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

When :ref:`subscenarios <subscenarios>` are executed, lines of '|' characters highlight the nestings of scenario executions.

Example of output from the `commutativeadditions.py <https://github.com/alxroyer/scenario/blob/master/demo/commutativeadditions.py>`_ sample test.

.. Subscenario output log example: 'commutativeadditions.py'.
.. literalinclude:: ../../data/commutativeadditions.log
    :language: none
    :end-at: EVIDENCE:   -> result1 = 2

*(Output truncated...)*

If a subscenario executes another subscenario, the '|' indentation is doubled, and so on.


.. _logging.indentation.class-logger:

Class logger indentation
^^^^^^^^^^^^^^^^^^^^^^^^

Additional indentation may be useful when the test makes verifications in a recursive way.

It may be set using the following methods:

- :py:meth:`scenario._logger.Logger.pushindentation()`,
- :py:meth:`scenario._logger.Logger.popindentation()`,
- :py:meth:`scenario._logger.Logger.resetindentation()`.

When these calls are made on a class logger,
the logging lines of this class logger are indented the way below.

.. Step `LoggingScenario.step110()` python implementation.
.. literalinclude:: ../../../demo/loggingdemo.py
    :language: python
    :start-at: def step110
    :end-before: def step120
    :dedent:

.. Step `LoggingScenario.step110()` console output.
.. literalinclude:: ../../data/loggingdemo.log
    :language: none
    :start-at: STEP#4:
    :end-before: STEP#5:

.. admonition:: Additional indentation pattern
    :class: tip

    The :py:meth:`scenario._logger.Logger.pushindentation()` and :py:meth:`scenario._logger.Logger.popindentation()` methods
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

When :py:meth:`scenario._logger.Logger.pushindentation()`, :py:meth:`scenario._logger.Logger.popindentation()`
and :py:meth:`scenario._logger.Logger.resetindentation()` calls are made on the main logger,
it takes effect on every log lines:

- main logger and class logger loggings (from *DEBUG* to *ERROR* log levels),
- but also actions, expected results and evidence texts.

.. Step `LoggingScenario.step120()` python implementation.
.. literalinclude:: ../../../demo/loggingdemo.py
    :language: python
    :start-at: def step120
    :dedent:

.. Step `LoggingScenario.step120()` console output.
.. literalinclude:: ../../data/loggingdemo.log
    :language: none
    :start-at: STEP#5:
    :end-before: END OF 'demo/loggingdemo.py'

.. admonition:: Scenario stack v/s user indentation
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

Still, with f-strings, the resulting string is computed before it is passed to the :py:meth:`scenario._logger.Logger.debug()` method,
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
      - :py:class:`scenario._debugutils.DelayedStr`
      - Abstract class that defines a string which computation may be delayed.

        You may inherit from this base class for specific needs.
      -

    * -
      - :py:class:`scenario._debugutils.FmtAndArgs`
      - Describes a delayed string that should be built with format and arguments.

        The string can be prepared step by step, thanks to the :py:meth:`scenario._debugutils.FmtAndArgs.push()` method.

        The application of the arguments is delayed on time when needed.
      - .. code-block:: python

            _str = scenario.debug.FmtAndArgs("Hello, I'm %s", name)
            if profession:
                _str.push(" and I'm a %s", profession)
            _str.push(".")
            self.debug(_str)

    * - :py:func:`scenario._debugutils.saferepr()`
      - :py:class:`scenario._debugutils.SafeRepr`
      - Computes a *repr*-like string, but ensures a *not-too-long* string, possibly focused on certain parts,
        such computation being delayed as for the others.
      - .. code-block:: python

            self.debug(
                "%s in %s",
                scenario.debug.saferepr(searched),
                scenario.debug.saferepr(longtext, focus=searched),
            )

    * - :py:func:`scenario._debugutils.jsondump()`
      - :py:class:`scenario._debugutils.JsonDump`
      - Delays the dump computation for JSON data.
      - .. code-block:: python

            self.debug(
                "JSON data: %s", scenario.debug.jsondump(data, indent=2),
                extra={self.Extra.LONG_TEXT_MAX_LINES: 10},
            )

        .. tip:: :py:func:`scenario._debugutils.jsondump()` may basically be displayed as :ref:`long texts <logging.long-text>`.

    * - :py:func:`scenario._debugutils.callback()`
      - :py:class:`scenario._debugutils.CallbackStr`
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

The `scenario` logging feature provides a way to log long texts on several lines.

To do so, set the ``extra`` parameter with :py:const:`scenario._logextradata.LogExtraData.LONG_TEXT`
and/or :py:const:`scenario._logextradata.LogExtraData.LONG_TEXT_MAX_LINES` options
when logging some text:

.. code-block:: python

    self.debug(
        scenario.debug.jsondump(_json_data, indent=2),
        extra={
            self.Extra.LONG_TEXT: True,  # `True` or `False`
            self.Extra.LONG_TEXT_MAX_LINES: 10,  # `int` value.
        },
    )

.. note::
    :py:const:`scenario._logextradata.LogExtraData.LONG_TEXT_MAX_LINES` autoamtically enables :py:const:`scenario._logextradata.LogExtraData.LONG_TEXT`.

This feature has primarily been designed for debugging, but it works with the
:py:meth:`scenario._logger.Logger.info()`,
:py:meth:`scenario._logger.Logger.warning()` and
:py:meth:`scenario._logger.Logger.error()`
methods as well.


.. _logging.outfile:

File logging
------------

The `scenario` logging feature provides the ability to save the test log output into a file.

To do so, set the :ref:`scenario.log_file <config-db.scenario.log_file>` configuration value,
either with the ``–-config-value`` command line option, or within a configuration file.

The command line example below
disables the output in the console,
but saves it into the 'doc/data/commutativeaddition.log' file
(from the main directory of the `scenario` library):

.. code-block:: bash

    $ mkdir -p ./doc/data
    $ ./bin/run-test.py \
        --config-value "scenario.log_console" "0" \
        --config-value "scenario.log_file" "./doc/data/commutativeaddition.log" \
        ./demo/commutativeaddition.py
    $ cat ./doc/data/commutativeaddition.log

.. literalinclude:: ../../data/commutativeaddition.log
    :language: none

.. tip::

    The :ref:`scenario.log_file <config-db.scenario.log_file>` configuration value may also be set programmatically
    through the :py:meth:`scenario._configdb.ConfigDatabase.set()` method,
    as illustrated in the :ref:`launcher script extension <launcher.pre-post>` section.


.. _logging.extra-flags:

Extra flags
-----------

The :py:class:`scenario._logextradata.LogExtraData` define a set of flags
that can be set to specialize the behaviour of each :py:class:`scenario._logger.Logger`.

For instance, the :py:class:`scenario._scenariorunner.ScenarioRunner` and :py:class:`scenario._scenariostack.ScenarioStack` classes
disable the :py:const:`scenario._logextradata.LogExtraData.ACTION_RESULT_MARGIN` flag,
so that their related log lines remain aligned on the left whatever the current action / expected result context is.

Please, refer the following links for details on extra flags:

- :py:class:`scenario._logextradata.LogExtraData`
- :py:meth:`scenario._logger.Logger.setextraflag()`

.. warning::
    Setting extra flags on class loggers, or even worse on the main logger, may lead to unpredictable behaviours.

    Nevertheless, this advanced feature is provided as is.
    To be used with parsimony.
