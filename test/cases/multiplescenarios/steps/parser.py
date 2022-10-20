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

import enum
import json
import re
import typing

if typing.TYPE_CHECKING:
    from scenario.typing import JSONDict
import scenario.test

# Related steps:
from steps.commonargs import ExecCommonArgs
from steps.logparsing import LogParserStep


class ParseFinalResultsLog(LogParserStep):
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
        LogParserStep.__init__(self, exec_step)
        self.description = "Scenario results log output parsing"

        self._parse_state = ParseFinalResultsLog.ParseState.END_NOT_REACHED_YET  # type: ParseFinalResultsLog.ParseState

        self.json_total_stats = {}  # type: JSONDict
        self.json_scenario_stats = []  # type: typing.List[JSONDict]

    @property
    def doc_only(self):  # type: (...) -> typing.Optional[bool]
        """
        Shortcut to *doc-only* mode.
        """
        return self.getexecstep(ExecCommonArgs).doc_only

    def _setparsestate(
            self,
            parse_state,  # type: ParseFinalResultsLog.ParseState
    ):  # type: (...) -> None
        self._debuglineinfo("%s -> %s" % (repr(self._parse_state), repr(parse_state)))
        self._parse_state = parse_state

    def _parseline(
            self,
            line,  # type: bytes
    ):  # type: (...) -> bool
        if re.match(rb' *---+$', line):
            # Skip the separation lines.
            return True

        _match = None  # type: typing.Optional[typing.Match[bytes]]

        if self._parse_state == ParseFinalResultsLog.ParseState.END_NOT_REACHED_YET:
            if re.match(rb'(INFO) +TOTAL +Status +Steps +Actions +Results +Time$', line):
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
            if _match:
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
                self._debuglineinfo("Total statistics: %s" % json.dumps(self.json_total_stats))

                self._setparsestate(ParseFinalResultsLog.ParseState.TEST_CASE_STATS_LINES)

                return True

        if self._parse_state == ParseFinalResultsLog.ParseState.TEST_CASE_STATS_LINES:
            # New test case line.
            _match = re.match(
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
                }  # type: JSONDict
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
                self._debuglineinfo("Scenario statistics: %s" % json.dumps(_json_scenario_stats))

                return True

            # Known issue details.
            _match = re.match(
                rb''.join([
                    # Log level (1).
                    rb'(WARNING) +',
                    # Script path (2).
                    rb'([^ :]+):',
                    # Line (3).
                    rb'(\d+):',
                    # Qualified name (4).
                    rb'([^ :]+): ',
                    # Issue id (5)
                    rb'Issue (.+)! ',
                    # Error message (6)
                    rb'(.+)',
                    # End of line.
                    rb'$',
                ]),
                line,
            )
            if _match:
                _warning_error = {
                    "type": "known-issue",
                    "id": self.tostr(_match.group(5)),
                    "message": self.tostr(_match.group(6)),
                    "location": self.tostr(b'%s:%s:%s' % (_match.group(2), _match.group(3), _match.group(4))),
                }  # type: JSONDict
                assert self.json_scenario_stats, "No current scenario"
                self.json_scenario_stats[-1]["warnings"].append(_warning_error)
                self._debuglineinfo("Warning: %s" % json.dumps(_warning_error))

                return True

            # Error details.
            _match = re.match(
                rb''.join([
                    # Log level (1).
                    rb'(ERROR) +',
                    # Script path (2).
                    rb'([^ :]+):',
                    # Line (3).
                    rb'(\d+):',
                    # Qualified name (4).
                    rb'([^ :]+): ',
                    # Error type (5)
                    rb'([^ :]+): ',
                    # Error message (6)
                    rb'(.+)',
                    # End of line.
                    rb'$',
                ]),
                line,
            )
            if _match:
                _json_error = {
                    "type": self.tostr(_match.group(5)),
                    "message": self.tostr(_match.group(6)),
                    "location": self.tostr(b'%s:%s:%s' % (_match.group(2), _match.group(3), _match.group(4))),
                }  # type: JSONDict
                assert self.json_scenario_stats, "No current scenario"
                self.json_scenario_stats[-1]["errors"].append(_json_error)
                self._debuglineinfo("Error: %s" % json.dumps(_json_error))

                return True

        return super()._parseline(line)
