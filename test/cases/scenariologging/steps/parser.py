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

import re
import typing

import scenario
import scenario.test
import scenario.text
if typing.TYPE_CHECKING:
    from scenario._typing import JsonDictType  # noqa  ## Access to protected module

from steps.logparsing import LogParserStep  # `LogParserStep` used for inheritance.


class ParseScenarioLog(LogParserStep):

    PARSE_STATE = "<parse-state>"  # type: str

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
    ):  # type: (...) -> None
        LogParserStep.__init__(self, exec_step)
        self.description = "Scenario log output parsing"

        # Initialize the scenario stack.
        self._json_scenario_stack = []  # type: typing.List[JsonDictType]
        # Then create the first scenario.
        self.json_main_scenario = self._newscenario()  # type: JsonDictType

    def _newscenario(self):  # type: (...) -> JsonDictType
        _json_new_scenario = {
            "name": None,
            "attributes": {},
            "steps": [],
            "status": "",
            "errors": [],
            "warnings": [],
            "time": {"start": None, "end": None, "elapsed": None},
            "stats": {
                "steps": {"executed": 0, "total": 0},
                "actions": {"executed": 0, "total": 0},
                "results": {"executed": 0, "total": 0},
            },
            ParseScenarioLog.PARSE_STATE: "",
        }  # type: JsonDictType

        # Check the current stack in order to determine whether it is a subscenario.
        if self._json_scenario_stack:
            # Subscenario do not give explicitly their status.
            # Consider it is SUCCESS by default.
            _json_new_scenario["status"] = "SUCCESS"
            # Register the scenario in the current action/result.
            assert self._json_scenario_stack[-1]["steps"], "No current step, cannot add subscenario"
            assert self._json_scenario_stack[-1]["steps"][-1]["actions-results"], "No current action/result, cannot add subscenario"
            self._json_scenario_stack[-1]["steps"][-1]["actions-results"][-1]["subscenarios"].append(_json_new_scenario)
        # Put the new scenario data on top of the scenario stack.
        self._json_scenario_stack.append(_json_new_scenario)

        return _json_new_scenario

    def _getscenario(
            self,
            match,  # type: ParseScenarioLog._Match
    ):  # type: (...) -> JsonDictType
        """
        Retrieves the JSON data corresponding to the scenario with the given indentation.

        :param match: Match instance, which first group gives the scenario stack indentation.
        :return: Scenario JSON data.
        """
        # Determine the stack index from the indentation.
        _stack_index = match.indentationlevel()  # type: int

        # Extend the scenario stack if needed.
        while len(self._json_scenario_stack) < _stack_index + 1:
            # Create new scenario data.
            self._newscenario()
            match.debug("New scenario added")

        # Reduce the stack if needed.
        while len(self._json_scenario_stack) > _stack_index + 1:
            match.debug("Removing last scenario from stack")
            self._json_scenario_stack.pop(-1)

        # Eventually return the scenario on top of the stack.
        assert self._json_scenario_stack, "No current scenario"
        return self._json_scenario_stack[-1]

    class _Match:
        def __init__(
                self,
                step,  # type: LogParserStep
                match,  # type: typing.Match[bytes]
        ):  # type: (...) -> None
            self.step = step  # type: LogParserStep
            self._match = match  # type: typing.Match[bytes]

        def __repr__(self):  # type: () -> str
            return repr(self._match)

        def indentation(self):  # type: (...) -> bytes
            return self._match.group(1)

        def indentationlevel(self):  # type: (...) -> int
            from scenario._scenariologging import ScenarioLogging  # noqa  ## Access to protected module

            return self.indentation().count(self.step.tobytes(ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN))

        def group(
                self,
                index,  # type: int
        ):  # type: (...) -> bytes
            if index <= 0:
                return self._match.group(index)
            else:
                return self._match.group(index + 2)

        def debug(
                self,
                message,  # type: str
                *fmt_args,  # type: typing.Any
        ):  # type: (...) -> None
            if len(fmt_args) > 0:
                self.step._debuglineinfo(  # noqa  ## Access to a protected member
                    "scenario_stack[%d]: " + message, self.indentationlevel(), *fmt_args,
                )
            else:
                # In case `message` contains bad format specifications...
                self.step._debuglineinfo(  # noqa  ## Access to a protected member
                    "scenario_stack[%d]: " + "%s", self.indentationlevel(), message,
                )

    def _match(
            self,
            regex,  # type: bytes
            line,  # type: bytes
    ):  # type: (...) -> typing.Optional[ParseScenarioLog._Match]
        from scenario._scenariologging import ScenarioLogging  # noqa  ## Access to protected module

        _match = re.search(
            rb''.join([
                # Scenario stack indentation
                rb'((%s)*)' % self.tobytes(ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN.replace("|", r"\|")),
                # Following of the regex.
                regex,
            ]),
            line,
        )  # type: typing.Optional[typing.Match[bytes]]
        if _match:
            return ParseScenarioLog._Match(self, _match)
        return None

    def _parseline(
            self,
            line,  # type: bytes
    ):  # type: (...) -> bool
        from scenario._scenariologging import ScenarioLogging  # noqa  ## Access to protected module

        # Useful typed variables.
        _match = None  # type: typing.Optional[ParseScenarioLog._Match]
        _error_level = ""  # type: str

        if self._match(rb'---+$', line):
            return True
        if line.endswith(self.tobytes(ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN.rstrip())):
            return True

        # Beginning of scenario.
        _match = self._match(rb'SCENARIO \'(.+)\'$', line)
        if _match:
            self._getscenario(_match)["name"] = self.tostr(_match.group(1))
            self._setparsestate(_match, f"SCENARIO '{self._getscenario(_match)['name']}'")
            _match.debug("Scenario: name=%r", self._getscenario(_match)["name"])
            return True

        # Scenario attribute.
        # Note: Control the number of leading spaces in order to discriminate with ACTION and RESULT lines.
        _match = self._match(rb'( *)([^ :]+): (.+)$', line)
        if _match and (_match.group(1) == b'  '):
            if self._getparsestate(_match).startswith("SCENARIO "):
                _attr_name = self.tostr(_match.group(2))  # type: str
                _attr_value = self.tostr(_match.group(3))  # type: str
                self._getscenario(_match)["attributes"][_attr_name] = _attr_value
                _match.debug("Scenario attribute: %s=%r", _attr_name, _attr_value)
                return True

        # Beginning of step.
        _match = self._match(rb'STEP#(\d+): (.+) \(([^:]+):(\d+):([^:]+)\)$', line)
        if _match:
            _json_step = {
                "number": self.tostr(_match.group(1)),
                "name": self.tostr(_match.group(5)),
                "description": self.tostr(_match.group(2)),
                "actions-results": [],
            }  # type: JsonDictType
            self._getscenario(_match)["steps"].append(_json_step)
            self._setparsestate(_match, f"STEP '{_json_step['name']}'")
            _match.debug("Step: name=%r, description=%r", _json_step["name"], _json_step["description"])
            return True

        # Action / expected result.
        _match = self._match(rb' +(ACTION|RESULT): *(.+)$', line)
        if _match:
            _json_action_result = {
                "type": self.tostr(_match.group(1)),
                "description": self.tostr(_match.group(2)),
                "subscenarios": [],
            }  # type: JsonDictType
            assert self._getscenario(_match)["steps"], "No current step, cannot add action/result"
            self._getscenario(_match)["steps"][-1]["actions-results"].append(_json_action_result)
            self._setparsestate(_match, f"{_json_action_result['type'].upper()} {_json_action_result['description']!r}")
            _match.debug("%s: description=%r", _json_action_result["type"].upper(), _json_action_result["description"])
            return True

        # Errors.
        _match = self._match(rb' +ERROR +File "(.+)", line (\d+), in (.+)$', line)
        if _match:
            _traceback_path = scenario.Path(self.tostr(_match.group(1)))  # type: scenario.Path
            if (
                _traceback_path.is_relative_to(scenario.test.paths.MAIN_PATH)
                and (not _traceback_path.is_relative_to(scenario.test.paths.MAIN_PATH / "src"))
            ):
                self._getscenario(_match)["errors"].append({
                    "type": None,
                    "message": None,
                    "location": f"{_traceback_path}:{self.tostr(_match.group(2))}:{self.tostr(_match.group(3))}",
                })
                _match.debug("Error location: %s", self._getscenario(_match)["errors"][-1]["location"])
                return True
            else:
                _match.debug("Error location: '%s' (skipped)", _traceback_path)
                return True

        _match = self._match(rb' +ERROR +([^:]+): (.+)$', line)
        if _match:
            if (
                (not _match.group(1).endswith(b'  # location'))  # Avoid matching with '  # location: ' patterns.
                and self._getscenario(_match)["errors"]
                and (not self._getscenario(_match)["errors"][-1]["type"])
                and (not self._getscenario(_match)["errors"][-1]["message"])
            ):
                self._getscenario(_match)["errors"][-1]["type"] = self.tostr(_match.group(1))
                _match.debug("Error type: %s", self._getscenario(_match)["errors"][-1]["type"])
                self._getscenario(_match)["errors"][-1]["message"] = self.tostr(_match.group(2))
                _match.debug("Error message: %r", self._getscenario(_match)["errors"][-1]["message"])

                # Automatically consider the scenario is FAIL.
                self._getscenario(_match)["status"] = "FAIL"
                _match.debug("Scenario status: FAIL (automatically set)")
                return True

        # Known issues.
        _match = self._match(
            rb''.join([
                # Log level (1).
                rb' *(WARNING|ERROR) +',
                # Beginning of issue line.
                rb'Issue',
                # Issue level:
                rb'(\(%s\))?' % rb''.join([
                    # Name (4).
                    rb'((.+)=)?'
                    # `int` value (5).
                    rb'(\d+)',
                ]),
                # Issue id (6).
                rb' *(.+)?',
                # Error message (7).
                rb'! (.+)',
                # Location:
                rb' \(%s\)' % rb':'.join([
                    # Script path (8).
                    rb'(.+)',
                    # Line (9).
                    rb'(\d+)',
                    # Qualified name (10).
                    rb'([^ :]+)',
                ]),
                # End of line.
                rb'$',
            ]),
            line,
        )
        if _match:
            _known_issue = {
                "type": "known-issue",
                "message": self.tostr(_match.group(7)),
                "location": self.tostr(b'%s:%s:%s' % (_match.group(8), _match.group(9), _match.group(10))),
            }  # type: JsonDictType
            if _match.group(5):
                _known_issue["level"] = int(_match.group(5))
            if _match.group(6):
                _known_issue["id"] = self.tostr(_match.group(6))
            if self._getparsestate(_match).startswith("END OF "):
                _error_level = self.tostr(_match.group(1))  # Type already declared above.
                self._getscenario(_match)[_error_level.lower() + "s"].append(_known_issue)
                _match.debug("Known issue: %r", _known_issue)
            else:
                _match.debug("Known issue skipped: %r", _known_issue)
            return True

        # Error / known issue URL.
        _match = self._match(rb' *(WARNING|ERROR) +(http(s)?://.*)$', line)
        if _match:
            if self._getparsestate(_match).startswith("END OF "):
                _error_level = self.tostr(_match.group(1))  # Type already declared above.
                assert self._getscenario(_match)[_error_level.lower() + "s"], f"No current {_error_level.lower()}"
                self._getscenario(_match)[_error_level.lower() + "s"][-1]["url"] = self.tostr(_match.group(2))
                self._debuglineinfo(f"{_error_level.capitalize()} URL: {self.tostr(_match.group(2))}")
            else:
                self._debuglineinfo("Error / known issue URL skipped")

            return True

        # Evidence.
        _match = self._match(rb' +EVIDENCE: (.+)$', line)
        if _match:
            _match.debug("EVIDENCE: %r", self.tostr(_match.group(1)))
            return True

        # Log lines.
        _match = self._match(rb' +(INFO {3}|WARNING {0}|ERROR {2}):(.*)$', line)
        if _match:
            _match.debug("%s: %r", self.tostr(_match.group(1).strip()), self.tostr(_match.group(2).strip()))
            return True

        # End of scenario.
        _match = self._match(rb'END OF \'(.+)\'$', line)
        if _match:
            self._setparsestate(_match, f"END OF '{self.tostr(_match.group(1))}'")
            _match.debug("End of scenario: name=%r", self.tostr(_match.group(1)))
            return True

        # Status.
        _match = self._match(rb' *Status: (.+)$', line)
        if _match:
            self.json_main_scenario["status"] = self.tostr(_match.group(1))
            _match.debug("Status: %r", self.json_main_scenario["status"])
            return True

        # Statistics.
        for _stats_type in ("step", "action", "result"):  # type: str
            _match = self._match(rb' *Number of %ss: (\d+)$' % self.tobytes(_stats_type.upper()), line)
            if _match:
                _stats = {"executed": 0, "total": int(_match.group(1))}  # type: JsonDictType
                self.json_main_scenario["stats"][_stats_type + "s"] = _stats
                _match.debug("Number of %s: %d", scenario.text.pluralize(_stats_type.upper()), _stats["total"])
                return True
            _match = self._match(rb' *Number of %ss: (\d+)/(\d+)$' % self.tobytes(_stats_type.upper()), line)
            if _match:
                _stats = {"executed": int(_match.group(1)), "total": int(_match.group(2))}  # Type already declared above.
                self.json_main_scenario["stats"][_stats_type + "s"] = _stats
                _match.debug("Number of %s: %d/%d", scenario.text.pluralize(_stats_type.upper()), _stats["executed"], _stats["total"])
                return True

        _match = self._match(rb' *Time: (%s)$' % self.tobytes(scenario.datetime.DURATION_REGEX), line)
        if _match:
            self.json_main_scenario["time"]["elapsed"] = scenario.datetime.str2fduration(self.tostr(_match.group(1)))
            _match.debug("Time: %f s", self.json_main_scenario["time"]["elapsed"])
            return True

        return super()._parseline(line)

    def _getparsestate(
            self,
            match,  # type: ParseScenarioLog._Match
    ):  # type: (...) -> str
        return str(self._getscenario(match)[ParseScenarioLog.PARSE_STATE])

    def _setparsestate(
            self,
            match,  # type: ParseScenarioLog._Match
            state,  # type: str
    ):  # type: (...) -> None
        self._getscenario(match)[ParseScenarioLog.PARSE_STATE] = state
