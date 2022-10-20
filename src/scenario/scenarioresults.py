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

"""
Scenario results management.
"""

import logging
import typing

# `ScenarioExecution` used in method signatures.
from .scenarioexecution import ScenarioExecution


class ScenarioResults:
    """
    List of scenario execution results.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes an empty list.
        """
        #: List of :class:`ScenarioResult` instances.
        self._results = []  # type: typing.List[ScenarioExecution]

    def add(
            self,
            scenario_execution,  # type: ScenarioExecution
    ):  # type: (...) -> None
        """
        Adds a :class:`ScenarioResult` instance in the list.

        :param scenario_execution: Scenario execution instance.
        """
        self._results.append(scenario_execution)

    @property
    def count(self):  # type: (...) -> int
        """
        :return: Number of scenario execution results in the list.
        """
        return len(self._results)

    def display(self):  # type: (...) -> None
        """
        Displays the results of the scenario executions in the list.

        Designed to display convient information after :class:`.scenariologging.ScenarioLogging` and :class:`.campaignlogging.CampaignLogging` outputs.
        """
        from .datetimeutils import f2strduration
        from .loggermain import MAIN_LOGGER
        from .stats import ExecTotalStats

        _total_step_stats = ExecTotalStats()  # type: ExecTotalStats
        _total_action_stats = ExecTotalStats()  # type: ExecTotalStats
        _total_result_stats = ExecTotalStats()  # type: ExecTotalStats
        _total_time = 0.0  # type: float

        # Scan the results, sum them up, and determine the way to display them.
        _name_field_len = 20  # type: int
        _status_field_len = 10  # type: int
        _stat_field_len = 10  # type: int
        _time_field_len = len(f2strduration(0.0))  # type: int
        _successes = []  # type: typing.List[ScenarioExecution]
        _warnings = []  # type: typing.List[ScenarioExecution]
        _errors = []  # type: typing.List[ScenarioExecution]
        for _scenario_execution in self._results:  # type: ScenarioExecution
            _name_field_len = max(_name_field_len, len(_scenario_execution.definition.name))
            _status_field_len = max(_status_field_len, len(str(_scenario_execution.status)))
            _total_step_stats.add(_scenario_execution.step_stats)
            _total_action_stats.add(_scenario_execution.action_stats)
            _total_result_stats.add(_scenario_execution.result_stats)
            if _scenario_execution.time.elapsed is not None:
                _total_time += _scenario_execution.time.elapsed
            if _scenario_execution.errors:
                _errors.append(_scenario_execution)
            elif _scenario_execution.warnings:
                _warnings.append(_scenario_execution)
            else:
                _successes.append(_scenario_execution)
        _total_name_field = "%d tests, %d failed, %d with warnings" % (len(self._results), len(_errors), len(_warnings))  # type: str
        _name_field_len = max(_name_field_len, len(_total_name_field))
        _stat_field_len = max(_stat_field_len, len(str(_total_step_stats)), len(str(_total_action_stats)), len(str(_total_result_stats)))

        _fmt = ""
        _fmt += "%-" + str(_name_field_len) + "s "
        _fmt += "%+" + str(_status_field_len) + "s "
        _fmt += "%+" + str(_stat_field_len) + "s "
        _fmt += "%+" + str(_stat_field_len) + "s "
        _fmt += "%+" + str(_stat_field_len) + "s "
        _fmt += " " * (_stat_field_len - len("Actions"))  # Ensure regular spacing between columns.
        _fmt += "%-" + str(_time_field_len) + "s "
        _fmt += " " * (_stat_field_len - len("Actions"))  # Ensure regular spacing between columns.
        _fmt += "%s"  # Note: No width for the *extra info* column.

        MAIN_LOGGER.rawoutput("------------------------------------------------")
        MAIN_LOGGER.info(_fmt % (
            "TOTAL", "Status",
            "Steps", "Actions", "Results",
            "Time", "",  # Note: No title for the *extra info* column.
        ))
        MAIN_LOGGER.info(_fmt % (
            _total_name_field, "",
            str(_total_step_stats), str(_total_action_stats), str(_total_result_stats),
            f2strduration(_total_time), "",
        ))
        MAIN_LOGGER.rawoutput("------------------------------------------------")

        for _scenario_execution in _successes:
            self._displayscenarioline(logging.INFO, _fmt, _scenario_execution)
        for _scenario_execution in _warnings:
            self._displayscenarioline(logging.WARNING, _fmt, _scenario_execution)
        for _scenario_execution in _errors:
            self._displayscenarioline(logging.ERROR, _fmt, _scenario_execution)

    @staticmethod
    def _displayscenarioline(
            log_level,  # type: int
            fmt,  # type: str
            scenario_execution,  # type: ScenarioExecution
    ):  # type: (...) -> None
        """
        Displays a scenario line.

        :param log_level: Log level to use for.
        :param fmt: Format to use.
        :param scenario_execution: Scenario to display.
        """
        from .datetimeutils import f2strduration
        from .loggermain import MAIN_LOGGER
        from .scenarioconfig import SCENARIO_CONFIG
        from .testerrors import TestError

        # Build extra info.
        _extra_info = []  # type: typing.List[str]
        for _attribute_name in SCENARIO_CONFIG.resultsextrainfo():  # type: str
            if _attribute_name in scenario_execution.definition.getattributenames():
                _extra_info.append(str(scenario_execution.definition.getattribute(_attribute_name)))

        # Log the scenario line.
        MAIN_LOGGER.log(log_level, fmt % (
            scenario_execution.definition.name, scenario_execution.status,
            str(scenario_execution.step_stats), str(scenario_execution.action_stats), str(scenario_execution.result_stats),
            f2strduration(scenario_execution.time.elapsed), ", ".join(_extra_info),
        ))

        # Display warnings, then errors.
        for _warning in scenario_execution.warnings:  # type: TestError
            if _warning.location:
                MAIN_LOGGER.warning("  %s: %s" % (_warning.location.tolongstring(), str(_warning)))
            else:
                MAIN_LOGGER.warning("  %s" % str(_warning))
        for _error in scenario_execution.errors:  # type: TestError
            if _error.location:
                MAIN_LOGGER.error("  %s: %s" % (_error.location.tolongstring(), str(_error)))
            else:
                MAIN_LOGGER.error("  %s" % str(_error))


__doc__ += """
.. py:attribute:: SCENARIO_RESULTS

    Main instance of :class:`ScenarioResults`.
"""
SCENARIO_RESULTS = ScenarioResults()  # type: ScenarioResults
