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


.. _handlers:

Handlers
========

The `scenario` framework provides a service that triggers handlers on events.


.. _handlers.handler-registration:

Handler registration
--------------------

First of all, declare your handler function:

.. scenario.Event.ERROR handler definition
.. literalinclude:: ../../demo/handlers.py
    :language: python
    :lines: 18-20

Then the handlers may be installed by calling the :py:meth:`scenario.handlers.Handlers.install()` method
on the :py:attr:`scenario.handlers` manager:

.. scenario.Event.ERROR handler installation
.. literalinclude:: ../../demo/handlers.py
    :language: python
    :lines: 50

.. tip::
    The event may be passed as an enum constant or a string.

    Using enums is usually a better option in as much as they can be type checked in camparison with simple strings.

The :py:meth:`scenario.handlers.Handlers.install()` method has a couple of parameters that specialize the way the handlers live and are triggered:

:scenario:
    Related scenario, if any.

    When this reference is set, the handler will be triggered only if the current scenario is the given scenario.
:once:
    *Once* flag.

    Makes this scenario be triggered once, and then uninstalled.
:first:
    Make this handler be called prior to other handlers when the event is met,
    otherwise the handler is called after the other handlers already registered for the given event.

The handlers may be uninstalled thanks to the :py:meth:`scenario.handlers.Handlers.uninstall()` method.


.. _handlers.scenario-events:

Scenario events
---------------

The following tables describes the `scenario` events that can be used to register handlers for.

.. tip::

    Use the :py:class:`scenario.Event` shortcut to the internal :py:class:`scenario.scenarioevents.ScenarioEvent` enum
    from `scenario` user code.

.. list-table:: Events raised during a scenario execution
    :widths: auto
    :header-rows: 1
    :stub-columns: 0

    * - Event
      - Description
      - Data type
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.BEFORE_TEST` = "scenario.before-test"
      - *Before test* handlers: handlers that are executed at the beginning of the scenario.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.Scenario`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.BEFORE_STEP` = "scenario.before-step"
      - *Before step* handlers: handlers that are executed before each step.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.Step`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.ERROR` = "scenario.error"
      - Error handler: handlers that are executed on test errors.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.Error`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.AFTER_STEP` = "scenario.after-step"
      - *After step* handlers: handlers that are executed after each step.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.Step`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.AFTER_TEST` = "scenario.after-test"
      - *After test* handlers: handlers that are executed at the end of the scenario.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.Scenario`

.. list-table:: Events raised during a campaign execution
    :widths: auto
    :header-rows: 1
    :stub-columns: 0

    * - Event
      - Description
      - Data type
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.BEFORE_CAMPAIGN` = "scenario.before-campaign"
      - *Before campaign* handlers: handlers that are executed at the beginning of the campaign.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.Campaign`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.BEFORE_TEST_SUITE` = "scenario.before-test-suite"
      - *Before test suite* handlers: handlers that are executed at the beginning of each test suite.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.TestSuite`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.BEFORE_TEST_CASE` = "scenario.before-test-case"
      - *Before test case* handlers: handlers that are executed at the beginning of each test case.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.TestCase`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.ERROR` = "scenario.error"
      - Error handler: handlers that are executed on test errors.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.Error`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.AFTER_TEST_CASE` = "scenario.after-test-case"
      - *After test case* handlers: handlers that are executed after each test case.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.TestCase`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.AFTER_TEST_SUITE` = "scenario.after-test-suite"
      - *After test suite* handlers: handlers that are executed after each test suite.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.TestSuite`
    * - :py:attr:`scenario.scenarioevents.ScenarioEvent.AFTER_CAMPAIGN` = "scenario.after-campaign"
      - *After campaign* handlers: handlers that are executed after the campaign.
      - :py:class:`scenario.scenarioevents.ScenarioEventData.Campaign`


.. _handlers.user-events:

User events
-----------

Even though the handler service is basically provided to let user code react on :ref:`scenario events <handlers.scenario-events>`,
it is made as a general feature so that it can be used for other purposes.
This way, you may define your own set of events within your test environment for instance.

In order to do so, a good practice is to define your set of events with an enum,
so that they can be type checked.

.. UserEvent enum definition.
.. literalinclude:: ../../demo/handlers.py
    :language: python
    :lines: 33-34

Then use the :py:meth:`scenario.handlers.Handlers.callhandlers()` method
to make the registered handlers (matching their additional conditions in option) be called.
Pass on event data as a single objet, which can be whatever you want.

.. Call of UserEvent.FOO handlers.
.. literalinclude:: ../../demo/handlers.py
    :language: python
    :lines: 59

.. tip::
    Considering evolutivity concerns, event data should rather be set with:

    - dedicated objects, like :py:class:`scenario.scenarioevents.ScenarioEventData` proposes,
    - or more informal dictionaries, like the 'demo/handlers.py' sample does.
