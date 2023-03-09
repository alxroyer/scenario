# -*- coding: utf-8 -*-

# Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Handler management.
"""

import enum
import typing

from ._logger import Logger  # `Logger` used for inheritance.

if typing.TYPE_CHECKING:
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


if typing.TYPE_CHECKING:
    #: Event specification type.
    #:
    #: Simple string or `enum`.
    EventType = typing.Union[str, enum.Enum]

    #: Handler type.
    #:
    #: :param: The event name as a simple string.
    #: :return: The second argument gives the event data.
    HandlerType = typing.Callable[[str, typing.Any], None]


class Handler:
    """
    Handler storage.
    """

    def __init__(
            self,
            event,  # type: EventType
            handler,  # type: HandlerType
            scenario_definition,  # type: typing.Optional[_ScenarioDefinitionType]
            once,  # type: bool
    ):  # type: (...) -> None
        """
        :param event: Event triggered.
        :param handler: Handler function.
        :param scenario_definition: Related scenario, if any.
        :param once: *Once* flag.
        """
        #: Event triggered.
        self.event = event  # type: EventType
        #: Handler function.
        self.handler = handler  # type: HandlerType
        #: Related scenario, if any.
        self.scenario_definition = scenario_definition  # type: typing.Optional[_ScenarioDefinitionType]
        #: *Once* flag.
        self.once = once  # type: bool


class Handlers(Logger):
    """
    Handler manager.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes an empty handler list.
        """
        from ._debugclasses import DebugClass

        Logger.__init__(self, log_class=DebugClass.HANDLERS)

        #: Installed handlers.
        #:
        #: Dictionary that associates events with their related handler list.
        self._handlers = {}  # type: typing.Dict[str, typing.List[Handler]]

    def install(
            self,
            event,  # type: EventType
            handler,  # type: HandlerType
            scenario=None,  # type: _ScenarioDefinitionType
            once=False,  # type: bool
            first=False,  # type: bool
    ):  # type: (...) -> None
        """
        Installs a handler.

        :param event: Event triggered.
        :param handler: Handler function.
        :param scenario: Related scenario definition, if any.
        :param once: *Once* flag.
        :param first:
            ``True`` to install this handler at the head of the list attached with the event given.

            .. warning:: Does not prevent a later handler to be installed before this one.
        """
        from ._enumutils import enum2str

        event = enum2str(event)

        self.debug("Installing *%s* handler %r, scenario=%r, once=%r, first=%r", event, handler, scenario, once, first)

        if event not in self._handlers:
            self._handlers[event] = []
        _new_handler = Handler(event, handler, scenario, once)  # type: Handler
        if first:
            self._handlers[event].insert(0, _new_handler)
        else:
            self._handlers[event].append(_new_handler)

    def uninstall(
            self,
            event,  # type: EventType
            handler,  # type: HandlerType
    ):  # type: (...) -> None
        """
        Removes the handler.

        :param event: Event triggered.
        :param handler: Handler function.
        """
        from ._enumutils import enum2str

        event = enum2str(event)

        self.debug("Removing *%s* handler %r", event, handler)

        if event in self._handlers:
            for _handler in self._handlers[event]:  # type: Handler
                # Don't use the `is` operator, otherwise bound methods may not behave as expected
                # (see https://stackoverflow.com/questions/41900639/python-unable-to-compare-bound-method-to-itself#41900748).
                if _handler.handler == handler:
                    self._handlers[event].remove(_handler)
                    return
        self.debug("No *%s* handler %r removed", event, handler)

    def callhandlers(
            self,
            event,  # type: EventType
            data,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Calls applicable handlers for the given event.

        :param event: Event met.
        :param data: Event data to pass on when calling each handler.
        """
        from ._enumutils import enum2str
        from ._scenariostack import SCENARIO_STACK

        event = enum2str(event)

        self.debug("Executing *%s* handlers", event)
        if event in self._handlers:
            for _handler in self._handlers[event].copy():  # type: Handler
                if _handler.scenario_definition and (not SCENARIO_STACK.iscurrentscenario(_handler.scenario_definition)):
                    self.debug("Handler %r skipped because the '%s' scenario is not being executed (or the current scenario is a subscenario)",
                               _handler.handler, _handler.scenario_definition.name)
                    continue

                try:
                    self.debug("Calling *%s* handler %r", event, _handler.handler)
                    _handler.handler(event, data)
                except Exception as _err:
                    self.warning(f"Handler exception: {_err}", exc_info=True)

                if _handler.once:
                    self.debug("%r expected to be called once, removing handler", _handler.handler)
                    if _handler in self._handlers[event]:
                        self._handlers[event].remove(_handler)


__doc__ += """
.. py:attribute:: HANDLERS

    Main instance of :class:`Handlers`.
"""
HANDLERS = Handlers()  # type: Handlers
