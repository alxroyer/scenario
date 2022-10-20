# -*- coding: utf-8 -*-

import enum

import scenario


def _beforetest(event, data):
    assert isinstance(data, scenario.EventData.Scenario)
    scenario.logging.debug(f"{event!r} handler called with test {data.scenario!r}")


def _beforestep(event, data):
    assert isinstance(data, scenario.EventData.Step)
    scenario.logging.debug(f"{event!r} handler called with step {data.step!r}")


def _error(event, data):
    assert isinstance(data, scenario.EventData.Error)
    scenario.logging.debug(f"{event!r} handler called with error {data.error!r}")


def _afterstep(event, data):
    assert isinstance(data, scenario.EventData.Step)
    scenario.logging.debug(f"{event!r} handler called with step {data.step!r}")


def _aftertest(event, data):
    assert isinstance(data, scenario.EventData.Scenario)
    scenario.logging.debug(f"{event!r} handler called with test {data.scenario!r}")


class UserEvent(enum.Enum):
    FOO = "foo"


def _foo(event, data):
    scenario.logging.debug(f"{event!r} handler called with {data!r}")


class Handlers(scenario.Scenario):

    SHORT_TITLE = "Handler demonstration"
    TEST_GOAL = "Register handlers and show their effect."

    def __init__(self):
        scenario.Scenario.__init__(self)
        scenario.handlers.install(scenario.Event.BEFORE_TEST, _beforetest)
        scenario.handlers.install(scenario.Event.BEFORE_STEP, _beforestep)
        scenario.handlers.install(scenario.Event.ERROR, _error)
        scenario.handlers.install(scenario.Event.AFTER_STEP, _afterstep)
        scenario.handlers.install(scenario.Event.AFTER_TEST, _aftertest)
        scenario.handlers.install(UserEvent.FOO, _foo)

    def step010(self):
        self.STEP("`UserEvent.FOO` event triggering")

        if self.ACTION("Trigger the `UserEvent.FOO` event, with the following parameters: a=1 and b='bar'."):
            scenario.handlers.callhandlers(UserEvent.FOO, {"a": 1, "b": "bar"})

    def step020(self):
        self.STEP("`UserEvent.FOO` event triggering")

        if self.ACTION("Trigger the `UserEvent.FOO` event, with the following parameters: a=2 and b='baz'."):
            scenario.handlers.callhandlers(UserEvent.FOO, {"a": 2, "b": "baz"})
