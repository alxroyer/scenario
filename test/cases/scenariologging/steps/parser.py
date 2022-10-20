# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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
if typing.TYPE_CHECKING:
    from scenario.typing import JSONDict
import scenario.test

# Related steps:
from steps.logparsing import LogParserStep


class ParseScenarioLog(LogParserStep):

    PARSE_STATE = "<parse-state>"  # type: str

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
    ):  # type: (...) -> None
        LogParserStep.__init__(self, exec_step)
        self.description = "Scenario log output parsing"

        # Initialize the scenario stack.
        self._json_scenario_stack = []  # type: typing.List[JSONDict]
        # Then create the first scenario.
        self.json_main_scenario = self._newscenario()  # type: JSONDict

    def _newscenario(self):  # type: (...) -> JSONDict
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
        }  # type: JSONDict

        # Check the current stack in order to determine whether it is a sub-scenario.
        if self._json_scenario_stack:
            # Sub-scenario do not give explicitely their status.
            # Consider it is SUCCESS by default.
            _json_new_scenario["status"] = "SUCCESS"
            # Register the scenario in the current action/result.
            assert self._json_scenario_stack[-1]["steps"], "No current step, cannot add sub-scenario"
            assert self._json_scenario_stack[-1]["steps"][-1]["actions-results"], "No current action/result, cannot add sub-scenario"
            self._json_scenario_stack[-1]["steps"][-1]["actions-results"][-1]["subscenarios"].append(_json_new_scenario)
        # Put the new scenario data on top of the scenario stack.
        self._json_scenario_stack.append(_json_new_scenario)

        return _json_new_scenario

    def _getscenario(
            self,
            match,  # type: typing.Match[bytes]
    ):  # type: (...) -> JSONDict
        """
        Retrieves the JSON data corresponding to the scenario with the given indentation.

        :param match: Match instance, which first group gives the scenario stack indentation.
        :return: Scenario JSON data.
        """
        from scenario.scenariologging import ScenarioLogging

        # Determine the stack index from the indentation.
        _stack_index = 0  # type: int
        _indentation = match.group(1)  # type: bytes
        if _indentation:
            _stack_index = _indentation.count(self.tobytes(ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN))

        # Extend the scenario stack if needed.
        while len(self._json_scenario_stack) < _stack_index + 1:
            # Create new scenario data.
            self._newscenario()

        # Reduce the stack if needed.
        while len(self._json_scenario_stack) > _stack_index + 1:
            self._json_scenario_stack.pop(-1)

        # Eventually return the scenario on top of the stack.
        assert self._json_scenario_stack, "No current scenario"
        return self._json_scenario_stack[-1]

    def _match(
            self,
            regex,  # type: bytes
            line,  # type: bytes
    ):  # type: (...) -> typing.Optional[typing.Match[bytes]]
        """
        When the line matches, the first group gives the scenario stack identation.
        Other groups start from 2.
        """
        from scenario.scenariologging import ScenarioLogging

        return re.match(
            rb''.join([
                # Beginning of line.
                rb'^',
                # Scenario stack indentation
                rb'(%s)*' % self.tobytes(ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN.replace("|", r"\|")),
                # Following of the regex.
                regex,
            ]),
            line,
        )

    def _debugdata(
            self,
            match,  # type: typing.Match[bytes]
            message,  # type: str
    ):  # type: (...) -> None
        self._debuglineinfo("%s%s" % (self.tostr(match.group(1) or b''), message))

    def _parseline(
            self,
            line,  # type: bytes
    ):  # type: (...) -> bool
        from scenario.scenariologging import ScenarioLogging

        if self._match(rb'---+$', line):
            return True
        if line.endswith(self.tobytes(ScenarioLogging.SCENARIO_STACK_INDENTATION_PATTERN.rstrip())):
            return True

        _match = None  # type: typing.Optional[typing.Match[bytes]]

        # Beginning of scenario.
        _match = self._match(rb'SCENARIO \'(.+)\'$', line)
        if _match:
            self._getscenario(_match)["name"] = self.tostr(_match.group(2))
            self._setparsestate(_match, "SCENARIO '%s'" % self._getscenario(_match)["name"])
            self._debugdata(_match, "Scenario: name='%s'" % self._getscenario(_match)["name"])
            return True

        # Scenario attribute.
        _match = self._match(rb'  ([^ :]+): (.+)$', line)
        if _match:
            if self._getparsestate(_match).startswith("SCENARIO "):
                _attr_name = self.tostr(_match.group(2))  # type: str
                _attr_value = self.tostr(_match.group(3))  # type: str
                self._getscenario(_match)["attributes"][_attr_name] = _attr_value
                self._debugdata(_match, "Scenario attribute: %s='%s'" % (_attr_name, _attr_value))
                return True

        # Beginning of step.
        _match = self._match(rb'STEP#(\d+): (.+) \((.+):([0-9]+):(.+)\)$', line)
        if _match:
            _json_step = {
                "number": self.tostr(_match.group(2)),
                "name": self.tostr(_match.group(6)),
                "description": self.tostr(_match.group(3)),
                "actions-results": [],
            }  # type: JSONDict
            self._getscenario(_match)["steps"].append(_json_step)
            self._setparsestate(_match, "STEP '%s'" % _json_step["name"])
            self._debugdata(_match, "Step: name='%s', description='%s'" % (_json_step["name"], _json_step["description"]))
            return True

        # Action / expected result.
        _match = self._match(rb' +(ACTION|RESULT): *(.+)$', line)
        if _match:
            _json_action_result = {
                "type": self.tostr(_match.group(2)),
                "description": self.tostr(_match.group(3)),
                "subscenarios": [],
            }  # type: JSONDict
            assert self._getscenario(_match)["steps"], "No current step, cannot add action/result"
            self._getscenario(_match)["steps"][-1]["actions-results"].append(_json_action_result)
            self._setparsestate(_match, "%s '%s'" % (_json_action_result["type"].upper(), _json_action_result["description"]))
            self._debugdata(_match, "%s: description='%s'" % (_json_action_result["type"].upper(), _json_action_result["description"]))
            return True

        # Errors
        _match = self._match(rb' +ERROR +File "(.+)", line (\d+), in (.+)$', line)
        if _match:
            _traceback_path = scenario.Path(self.tostr(_match.group(2)))  # type: scenario.Path
            if (
                _traceback_path.is_relative_to(scenario.test.paths.MAIN_PATH)
                and (not _traceback_path.is_relative_to(scenario.test.paths.MAIN_PATH / "src"))
            ):
                self._getscenario(_match)["errors"].append({
                    "type": None,
                    "message": None,
                    "location": "%s:%s:%s" % (_traceback_path, self.tostr(_match.group(3)), self.tostr(_match.group(4))),
                })
                self._debugdata(_match, "Error location: %s" % self._getscenario(_match)["errors"][-1]["location"])
                return True
            else:
                self._debugdata(_match, "Error location: '%s' (skipped)" % _traceback_path)
                return True

        _match = self._match(rb' +ERROR +([^:]+): (.+)$', line)
        if _match:
            if (
                (not _match.group(2).endswith(b'  # location'))  # Avoid matching with '  # location: ' patterns.
                and self._getscenario(_match)["errors"]
                and (not self._getscenario(_match)["errors"][-1]["type"])
                and (not self._getscenario(_match)["errors"][-1]["message"])
            ):
                self._getscenario(_match)["errors"][-1]["type"] = self.tostr(_match.group(2))
                self._debugdata(_match, "Error type: %s" % self._getscenario(_match)["errors"][-1]["type"])
                self._getscenario(_match)["errors"][-1]["message"] = self.tostr(_match.group(3))
                self._debugdata(_match, "Error message: %s" % self._getscenario(_match)["errors"][-1]["message"])

                # Automatically consider the scenario is FAIL.
                self._getscenario(_match)["status"] = "FAIL"
                self._debugdata(_match, "Scenario status: FAIL (automatically set)")
                return True

        # Known issues.
        _match = self._match(rb' *(WARNING|ERROR) +([^:]+):(\d+):([^:]+): Issue (.+)! (.+)$', line)
        if _match:
            _json_known_issue = {
                "type": "known-issue",
                "id": self.tostr(_match.group(6)),
                "message": self.tostr(_match.group(7)),
                "location": self.tostr(b'%s:%s:%s' % (_match.group(3), _match.group(4), _match.group(5))),
            }  # type: JSONDict
            if self._getparsestate(_match).startswith("END OF "):
                _error_level = self.tostr(_match.group(2))  # type: str
                self._getscenario(_match)[_error_level.lower() + "s"].append(_json_known_issue)
                self._debugdata(_match, "Known issue: %s" % repr(_json_known_issue))
            else:
                self._debugdata(_match, "Known issue skipped: %s" % repr(_json_known_issue))
            return True

        # Evidence.
        _match = self._match(rb' +EVIDENCE: (.+)$', line)
        if _match:
            self._debugdata(_match, "EVIDENCE: '%s'" % self.tostr(_match.group(2)))
            return True

        # Log lines.
        _match = self._match(rb' +(INFO {3}|WARNING {0}|ERROR {2}):(.*)$', line)
        if _match:
            self._debugdata(_match, "%s: '%s'" % (self.tostr(_match.group(2).strip()), self.tostr(_match.group(3).strip())))
            return True

        # End of scenario.
        _match = self._match(rb'END OF \'(.+)\'$', line)
        if _match:
            self._setparsestate(_match, "END OF '%s'" % self.tostr(_match.group(2)))
            self._debugdata(_match, "End of scenario: name='%s'" % self.tostr(_match.group(2)))
            return True

        # Status.
        _match = self._match(rb' *Status: (.+)$', line)
        if _match:
            self.json_main_scenario["status"] = self.tostr(_match.group(2))
            self._debugdata(_match, "Status: '%s'" % self.json_main_scenario["status"])
            return True

        # Statistics.
        for _stats_type in ("step", "action", "result"):  # type: str
            _match = self._match(rb' *Number of %ss: (\d+)$' % self.tobytes(_stats_type.upper()), line)
            if _match:
                _stats = {"executed": 0, "total": int(_match.group(2))}  # type: JSONDict
                self.json_main_scenario["stats"][_stats_type + "s"] = _stats
                self._debugdata(_match, "Number of %ss: %d" % (_stats_type.upper(), _stats["total"]))
                return True
            _match = self._match(rb' *Number of %ss: (\d+)/(\d+)$' % self.tobytes(_stats_type.upper()), line)
            if _match:
                _stats = {"executed": int(_match.group(2)), "total": int(_match.group(3))}  # Type already declared above.
                self.json_main_scenario["stats"][_stats_type + "s"] = _stats
                self._debugdata(_match, "Number of %ss: %d/%d" % (_stats_type.upper(), _stats["executed"], _stats["total"]))
                return True

        _match = self._match(rb' *Time: (\d+.\d+) s$', line)
        if _match:
            self.json_main_scenario["time"]["elapsed"] = float(_match.group(2))
            self._debugdata(_match, "Time: %f s" % self.json_main_scenario["time"]["elapsed"])
            return True

        return super()._parseline(line)

    def _getparsestate(
            self,
            match,  # type: typing.Match[bytes]
    ):  # type: (...) -> str
        return str(self._getscenario(match)[ParseScenarioLog.PARSE_STATE])

    def _setparsestate(
            self,
            match,  # type: typing.Match[bytes]
            state,  # type: str
    ):  # type: (...) -> None
        self._getscenario(match)[ParseScenarioLog.PARSE_STATE] = state
