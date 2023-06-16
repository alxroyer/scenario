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

import enum
import re
import typing

import scenario.test
if typing.TYPE_CHECKING:
    from scenario._typing import JsonDictType as _JsonDictType  # noqa  ## Access to protected module

if True:
    from steps.logparsing import LogParserStep as _LogParserStepImpl  # `LogParserStep` used for inheritance.


class ParseFinalResultsLog(_LogParserStepImpl):
    """
    Analyzes the end of the log output, and stores objects that represent what has been read.
    """

    class ParseState(enum.IntEnum):
        END_NOT_REACHED_YET = 0
        TOTAL_STATS_LINE = 1
        TEST_CASE_STATS_LINES = 2

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
    ):  # type: (...) -> None
        _LogParserStepImpl.__init__(self, exec_step)
        self.description = "Final results log output parsing"

        self._parse_state = ParseFinalResultsLog.ParseState.END_NOT_REACHED_YET  # type: ParseFinalResultsLog.ParseState

        self.json_total_stats = {}  # type: _JsonDictType
        self.json_scenario_stats = []  # type: typing.List[_JsonDictType]

    @property
    def doc_only(self):  # type: () -> typing.Optional[bool]
        """
        Shortcut to *doc-only* mode.
        """
        from steps.commonargs import ExecCommonArgs

        return self.getexecstep(ExecCommonArgs).doc_only

    def _setparsestate(
            self,
            parse_state,  # type: ParseFinalResultsLog.ParseState
    ):  # type: (...) -> None
        self._debuglineinfo("%r -> %r", self._parse_state, parse_state)
        self._parse_state = parse_state

    def _parseline(
            self,
            line,  # type: bytes
    ):  # type: (...) -> bool
        # Useful typed variables.
        _error_level = ""  # type: str
        _match = None  # type: typing.Optional[typing.Match[bytes]]

        if re.search(rb' *---+$', line):
            # Skip the separation lines.
            return True

        if self._parse_state == ParseFinalResultsLog.ParseState.END_NOT_REACHED_YET:
            if re.search(rb'(INFO) +TOTAL +Status +Steps +Actions +Results +Time$', line):
                self._debuglineinfo("Header line found")
                self._setparsestate(ParseFinalResultsLog.ParseState.TOTAL_STATS_LINE)
                return True
        if self._parse_state == ParseFinalResultsLog.ParseState.END_NOT_REACHED_YET:
            # Ignore lines until the end has been reached.
            return True

        if self._parse_state == ParseFinalResultsLog.ParseState.TOTAL_STATS_LINE:
            _match = self.assertregex(
                rb''.join([
                    # Log level (1).
                    rb'(INFO) +',
                    # Total number of tests (2).
                    rb'(\d+) tests, ',
                    # Number of tests in error (3).
                    rb'(\d+) failed, ',
                    # Number of tests with warnings (4).
                    rb'(\d+) with warnings +',
                    # Step statistics (5) or (5)/(6).
                    rb'(\d+) +' if self.doc_only else rb'(\d+)/(\d+) +',
                    # Action statistics (6) or (7)/(8).
                    rb'(\d+) +' if self.doc_only else rb'(\d+)/(\d+) +',
                    # Expected result statistics (7) or (9)/(10).
                    rb'(\d+) +' if self.doc_only else rb'(\d+)/(\d+) +',
                    # Time (8) or (11).
                    rb'(\d+:\d+:\d+\.\d+)',
                    # End of line.
                    rb'$',
                ]),
                line,
                err="Invalid line, should be the total statistics line",
            )
            self.json_total_stats = {
                "tests": {"total": int(_match.group(2)), "errors": int(_match.group(3)), "warnings": int(_match.group(4))},
                "steps": {"executed": None, "total": None},
                "actions": {"executed": None, "total": None},
                "results": {"executed": None, "total": None},
                "time": scenario.datetime.str2fduration(self.tostr(_match.group(8 if self.doc_only else 11))),
            }
            if self.doc_only:
                self.json_total_stats["steps"]["total"] = int(_match.group(5))
                self.json_total_stats["actions"]["total"] = int(_match.group(6))
                self.json_total_stats["results"]["total"] = int(_match.group(7))
            else:
                self.json_total_stats["steps"]["executed"] = int(_match.group(5))
                self.json_total_stats["steps"]["total"] = int(_match.group(6))
                self.json_total_stats["actions"]["executed"] = int(_match.group(7))
                self.json_total_stats["actions"]["total"] = int(_match.group(8))
                self.json_total_stats["results"]["executed"] = int(_match.group(9))
                self.json_total_stats["results"]["total"] = int(_match.group(10))
            self._debuglineinfo("Total statistics: %s", scenario.debug.jsondump(self.json_total_stats))

            self._setparsestate(ParseFinalResultsLog.ParseState.TEST_CASE_STATS_LINES)

            return True

        if self._parse_state == ParseFinalResultsLog.ParseState.TEST_CASE_STATS_LINES:
            # New test case line.
            _match = re.search(
                rb''.join([
                    # Log level (1).
                    rb'(INFO|WARNING|ERROR) +',
                    # Name (2).
                    rb'(.+) +',
                    # Status (3).
                    rb'(%s) +' % self.tobytes(r"|".join(scenario.ExecutionStatus)),
                    # Step statistics (4) or (4)/(5).
                    rb'(\d+) +' if self.doc_only else rb'(\d+)/(\d+) +',
                    # Action statistics (5) or (6)/(7).
                    rb'(\d+) +' if self.doc_only else rb'(\d+)/(\d+) +',
                    # Expected result statistics (6) or (8)/(9).
                    rb'(\d+) +' if self.doc_only else rb'(\d+)/(\d+) +',
                    # Time (7) or (10).
                    rb'(\d+:\d+:\d+\.\d+)',
                    # Extra info (9) or (12).
                    rb'(    |)(.+|)',
                    # End of line.
                    rb'$',
                ]),
                line,
            )
            if _match:
                _json_scenario_stats = {
                    "name": self.tostr(_match.group(2).strip()),
                    "status": self.tostr(_match.group(3)),
                    "steps": {"executed": None, "total": None},
                    "actions": {"executed": None, "total": None},
                    "results": {"executed": None, "total": None},
                    "time": scenario.datetime.str2fduration(self.tostr(_match.group(7 if self.doc_only else 10))),
                    "extra-info": self.tostr(_match.group(9 if self.doc_only else 12)),
                    "errors": [],
                    "warnings": [],
                }  # type: _JsonDictType
                if self.doc_only:
                    _json_scenario_stats["steps"]["total"] = int(_match.group(4))
                    _json_scenario_stats["actions"]["total"] = int(_match.group(5))
                    _json_scenario_stats["results"]["total"] = int(_match.group(6))
                else:
                    _json_scenario_stats["steps"]["executed"] = int(_match.group(4))
                    _json_scenario_stats["steps"]["total"] = int(_match.group(5))
                    _json_scenario_stats["actions"]["executed"] = int(_match.group(6))
                    _json_scenario_stats["actions"]["total"] = int(_match.group(7))
                    _json_scenario_stats["results"]["executed"] = int(_match.group(8))
                    _json_scenario_stats["results"]["total"] = int(_match.group(9))
                self.json_scenario_stats.append(_json_scenario_stats)
                self._debuglineinfo("Scenario statistics: %s", scenario.debug.jsondump(_json_scenario_stats))

                return True

            # Known issue details.
            _match = re.search(
                rb''.join([
                    # Log level (1).
                    rb'(WARNING|ERROR) +',
                    # Beginning of issue line.
                    rb'Issue',
                    # Issue level:
                    rb'(\(%s\))?' % rb''.join([
                        # Name (4).
                        rb'((.+)=)?',
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
                }  # type: _JsonDictType
                if _match.group(5):
                    _known_issue["level"] = int(_match.group(5))
                if _match.group(6):
                    _known_issue["id"] = self.tostr(_match.group(6))
                assert self.json_scenario_stats, "No current scenario"
                _error_level = self.tostr(_match.group(1))  # Type already declared above.
                self.json_scenario_stats[-1][_error_level.lower() + "s"].append(_known_issue)
                self._debuglineinfo("Known issue: %s", scenario.debug.jsondump(_known_issue))
                self._debuglineinfo(f"Number of {_error_level.lower()}s: {len(self.json_scenario_stats[-1][_error_level.lower() + 's'])}")

                return True

            # Error details.
            _match = re.search(
                rb''.join([
                    # Log level (1).
                    rb'(ERROR) +',
                    # Error type (2).
                    rb'([^ :]+): ',
                    # Error message (3).
                    rb'(.+) ',
                    # Location:
                    rb'\(%s\)' % rb':'.join([
                        # Script path (4).
                        rb'(.+)',
                        # Line (5).
                        rb'(\d+)',
                        # Qualified name (6).
                        rb'([^ :]+)',
                    ]),
                    # End of line.
                    rb'$',
                ]),
                line,
            )
            if _match:
                _json_error = {
                    "type": self.tostr(_match.group(2)),
                    "message": self.tostr(_match.group(3)),
                    "location": self.tostr(b'%s:%s:%s' % (_match.group(4), _match.group(5), _match.group(6))),
                }  # type: _JsonDictType
                assert self.json_scenario_stats, "No current scenario"
                self.json_scenario_stats[-1]["errors"].append(_json_error)
                self._debuglineinfo("Error: %s", scenario.debug.jsondump(_json_error))

                return True

        # Error / known issue URL.
        _match = re.search(rb'(WARNING|ERROR) +(http(s)?://.*)$', line)
        if _match:
            if self._parse_state == ParseFinalResultsLog.ParseState.TEST_CASE_STATS_LINES:
                _error_level = self.tostr(_match.group(1))  # Type already declared above.
                assert self.json_scenario_stats[-1][_error_level.lower() + "s"], f"No current {_error_level.lower()}"
                self.json_scenario_stats[-1][_error_level.lower() + "s"][-1]["url"] = self.tostr(_match.group(2))
                self._debuglineinfo(f"{_error_level.capitalize()} URL: {self.tostr(_match.group(2))}")
            else:
                self._debuglineinfo("Error / known issue URL skipped")

            return True

        return super()._parseline(line)
