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
Campaign execution management.
"""

import logging
import re
import sys
import time
import typing

# `CampaignExecution`, `CampaignExecution` and `TestSuiteExecution` used in method signatures.
from .campaignexecution import CampaignExecution, TestCaseExecution, TestSuiteExecution
# `ErrorCode` used in method signatures.
from .errcodes import ErrorCode
# `Logger` used for inheritance.
from .logger import Logger

if typing.TYPE_CHECKING:
    # `AnyPathType` used in method signatures.
    # Type declared for type checking only.
    from .path import AnyPathType


class CampaignRunner(Logger):
    """
    Campaign execution engine: runs test scenarios from input files.

    Only one instance, accessible through the :attr:`CAMPAIGN_RUNNER` singleton.

    This class works with the following helper classes, with their respected purpose:

    - :class:`.campaignargs.CampaignArgs`: command line arguments,
    - :class:`.campaignexecution.CampaignExecution`: object that describes a campaign execution,
    - :class:`.campaignlogging.CampaignLogging`: campaign execution logging,
    - :class:`.campaignreport.CampaignReport`: campaign report generation.
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures logging for the :class:`CampaignRunner` class.
        """
        from .debugclasses import DebugClass

        Logger.__init__(self, log_class=DebugClass.CAMPAIGN_RUNNER)

    def main(self):  # type: (...) -> ErrorCode
        """
        Campaign runner main function, as a member method.

        :return: Error code.
        """
        from .campaignargs import CampaignArgs
        from .campaignlogging import CAMPAIGN_LOGGING
        from .campaignreport import CAMPAIGN_REPORT
        from .datetimeutils import toiso8601
        from .handlers import HANDLERS
        from .loggermain import MAIN_LOGGER
        from .loggingservice import LOGGING_SERVICE
        from .path import Path
        from .scenarioevents import ScenarioEvent, ScenarioEventData
        from .scenarioresults import SCENARIO_RESULTS
        from .testerrors import ExceptionError

        try:
            # Analyze program arguments, if not already set.
            if not CampaignArgs.isset():
                CampaignArgs.setinstance(CampaignArgs())
                if not CampaignArgs.getinstance().parse(sys.argv[1:]):
                    return CampaignArgs.getinstance().error_code

            # Create the date/time output directory (if required).
            if CampaignArgs.getinstance().create_dt_subdir:
                _outdir_basename = toiso8601(time.time())[:len("XXXX-XX-XXTXX:XX:XX")].replace(":", "-").replace("T", "_")  # type: str
                _outdir = CampaignArgs.getinstance().outdir / _outdir_basename  # type: Path
            else:
                _outdir = CampaignArgs.getinstance().outdir
            _outdir.mkdir(parents=True, exist_ok=True)

            # Start log features.
            LOGGING_SERVICE.start()

            _campaign_execution = CampaignExecution(_outdir)  # type: CampaignExecution
            HANDLERS.callhandlers(ScenarioEvent.BEFORE_CAMPAIGN, ScenarioEventData.Campaign(campaign_execution=_campaign_execution))

            CAMPAIGN_LOGGING.begincampaign(_campaign_execution)
            _campaign_execution.time.setstarttime()

            for _test_suite_path in CampaignArgs.getinstance().test_suite_paths:  # type: Path
                _res = self._exectestsuitefile(_campaign_execution, _test_suite_path)  # type: ErrorCode
                if _res != ErrorCode.SUCCESS:
                    return _res

            _campaign_execution.time.setendtime()
            CAMPAIGN_REPORT.writejunitreport(_campaign_execution, _campaign_execution.junit_path)
            CAMPAIGN_LOGGING.endcampaign(_campaign_execution)

            HANDLERS.callhandlers(ScenarioEvent.AFTER_CAMPAIGN, ScenarioEventData.Campaign(campaign_execution=_campaign_execution))

            # Display final results.
            SCENARIO_RESULTS.display()

            # Terminate log features.
            LOGGING_SERVICE.stop()

            return ErrorCode.SUCCESS

        except Exception as _err:
            ExceptionError(_err).logerror(MAIN_LOGGER, logging.ERROR)
            return ErrorCode.INTERNAL_ERROR

    def _exectestsuitefile(
            self,
            campaign_execution,  # type: CampaignExecution
            test_suite_path,  # type: AnyPathType
    ):  # type: (...) -> ErrorCode
        """
        Executes a test suite file.

        :param campaign_execution: :class:`CampaignExecution` object to store results into.
        :param test_suite_path: Test suite file to execute.
        :return: Error code.
        """
        _test_suite_execution = TestSuiteExecution(campaign_execution, test_suite_path)  # type: TestSuiteExecution
        campaign_execution.test_suite_executions.append(_test_suite_execution)
        _res = self._exectestsuite(_test_suite_execution)  # type: ErrorCode

        return _res

    def _exectestsuite(
            self,
            test_suite_execution,  # type: TestSuiteExecution
    ):  # type: (...) -> ErrorCode
        """
        Executes a test suite.

        :param test_suite_execution: Test suite to execute.
        :return: Error code.
        """
        from .campaignlogging import CAMPAIGN_LOGGING
        from .handlers import HANDLERS
        from .path import Path
        from .scenarioevents import ScenarioEvent, ScenarioEventData

        HANDLERS.callhandlers(ScenarioEvent.BEFORE_TEST_SUITE, ScenarioEventData.TestSuite(test_suite_execution=test_suite_execution))

        CAMPAIGN_LOGGING.begintestsuite(test_suite_execution)
        test_suite_execution.time.setstarttime()

        _error_codes = []  # type: typing.List[ErrorCode]
        if not test_suite_execution.test_suite_file.read():
            _error_codes.append(ErrorCode.INPUT_FORMAT_ERROR)
        else:
            for _test_script_path in test_suite_execution.test_suite_file.script_paths:  # type: Path
                _test_case_execution = TestCaseExecution(test_suite_execution, _test_script_path)  # type: TestCaseExecution
                test_suite_execution.test_case_executions.append(_test_case_execution)

                _res = self._exectestcase(_test_case_execution)
                if _res != ErrorCode.SUCCESS:
                    break

        test_suite_execution.time.setendtime()
        CAMPAIGN_LOGGING.endtestsuite(test_suite_execution)

        HANDLERS.callhandlers(ScenarioEvent.AFTER_TEST_SUITE, ScenarioEventData.TestSuite(test_suite_execution=test_suite_execution))

        return ErrorCode.worst(_error_codes)

    def _exectestcase(
            self,
            test_case_execution,  # type: TestCaseExecution
    ):  # type: (...) -> ErrorCode
        """
        Executes a test case.

        :param test_case_execution: Test case to execute.
        :return: Error code.
        """
        from .campaignargs import CampaignArgs
        from .campaignlogging import CAMPAIGN_LOGGING
        from .configdb import CONFIG_DB
        from .confignode import ConfigNode
        from .datetimeutils import f2strduration, ISO8601_REGEX
        from .debugloggers import ExecTimesLogger
        from .handlers import HANDLERS
        from .path import Path
        from .scenarioconfig import SCENARIO_CONFIG
        from .scenariodefinition import ScenarioDefinition
        from .scenarioevents import ScenarioEvent, ScenarioEventData
        from .scenarioexecution import ScenarioExecution
        from .scenarioresults import SCENARIO_RESULTS
        from .subprocess import SubProcess
        from .testerrors import TestError

        _exec_times_logger = ExecTimesLogger("CampaignRunner._exectestcase()")  # type: ExecTimesLogger

        HANDLERS.callhandlers(ScenarioEvent.BEFORE_TEST_CASE, ScenarioEventData.TestCase(test_case_execution=test_case_execution))
        _exec_times_logger.tick("After *before-test-case* handlers")

        CAMPAIGN_LOGGING.begintestcase(test_case_execution)
        _exec_times_logger.tick("Starting test case")
        test_case_execution.time.setstarttime()

        # Prepare output paths.
        def _mkoutpath(
                ext,  # type: str
        ):  # type: (...) -> Path
            """
            Output file path builder.

            :param ext: Extension for the new file.
            :return: Output file path.
            """
            return test_case_execution.test_suite_execution.campaign_execution.outdir / (test_case_execution.script_path.stem + ext)

        test_case_execution.json.path = _mkoutpath(".json")
        test_case_execution.log.path = _mkoutpath(".log")

        # Prepare the command line.
        _subprocess = SubProcess(sys.executable, SCENARIO_CONFIG.runnerscriptpath())  # type: SubProcess
        # Report configuration files and single configuration values from campaign to scenario execution.
        for _config_path in CampaignArgs.getinstance().config_paths:  # type: Path
            _subprocess.addargs("--config-file", _config_path)
        for _config_name in CampaignArgs.getinstance().config_values:  # type: str
            _subprocess.addargs("--config-value", _config_name, CampaignArgs.getinstance().config_values[_config_name])
        # Report common execution options from campaign to scenario execution.
        CampaignArgs.reportexecargs(CampaignArgs.getinstance(), _subprocess)
        # --json-report option.
        _subprocess.addargs("--json-report", test_case_execution.json.path)
        # Log outfile specification.
        _subprocess.addargs("--config-value", str(SCENARIO_CONFIG.Key.LOG_FILE), test_case_execution.log.path)
        # No log console specification.
        _subprocess.addargs("--config-value", str(SCENARIO_CONFIG.Key.LOG_CONSOLE), "0")
        # Log date/time option propagation.
        _log_datetime_config = CONFIG_DB.getnode(SCENARIO_CONFIG.Key.LOG_DATETIME)  # type: typing.Optional[ConfigNode]
        if _log_datetime_config:
            _subprocess.addargs("--config-value", str(SCENARIO_CONFIG.Key.LOG_DATETIME), _log_datetime_config.cast(type=str))
        # Script path.
        _subprocess.addargs(test_case_execution.script_path)

        # In case no execution data is available in the end,
        # create `ScenarioDefinition` and `ScenarioExecution` instances from scratch in order to save error details.
        _fallback_errors = ScenarioDefinition()  # type: ScenarioDefinition
        _fallback_errors.name = test_case_execution.name
        _fallback_errors.execution = ScenarioExecution(_fallback_errors)
        _fallback_errors.execution.time.setstarttime()

        def _fallbackerror(
                error_message,  # type: str
        ):  # type: (...) -> None
            assert _fallback_errors.execution
            _fallback_errors.execution.errors.append(TestError(error_message))

        # Execute the scenario.
        _exec_times_logger.tick("Executing the sub-process")
        _subprocess.setlogger(self).run(timeout=SCENARIO_CONFIG.scenariotimeout())
        _exec_times_logger.tick("After sub-process execution")
        self.debug("%s returned %r", _subprocess, _subprocess.returncode)

        # Analyze scenario return code.
        if _subprocess.returncode is None:
            _fallbackerror(f"'{test_case_execution.script_path}' did not return within {_subprocess.time.elapsed} seconds")
        elif _subprocess.returncode != 0:
            try:
                _returncode_desc = str(ErrorCode(_subprocess.returncode))  # type: str
            except ValueError as _err:
                _returncode_desc = str(_err)  # Type already declared above.
            _fallbackerror(f"'{test_case_execution.script_path}' failed with error code {_subprocess.returncode!r} ({_returncode_desc})")
        _exec_times_logger.tick("After post-analyses")

        # Read the log outfile.
        if test_case_execution.log.path.is_file():
            # Don't bother with errors, keep going on.
            self.debug("Reading '%s'", test_case_execution.log.path)
            test_case_execution.log.read()
        else:
            self.debug("No such file '%s'", test_case_execution.log.path)
        _exec_times_logger.tick("After reading the log file")

        # Read the JSON outfile.
        if test_case_execution.json.path.is_file():
            # Don't bother with errors, keep going on.
            self.debug("Reading '%s'", test_case_execution.json.path)
            test_case_execution.json.read()
        else:
            self.debug("No such file '%s'", test_case_execution.json.path)
        _exec_times_logger.tick("After reading the JSON file")

        # Fix the scenario definition and execution instances, if not successfully read from the JSON report above.
        if not test_case_execution.scenario_execution:
            test_case_execution.json.content = _fallback_errors

            # Read error lines from stdout.
            if test_case_execution.log.content:
                for _stdout_line in test_case_execution.log.content.splitlines():  # type: bytes
                    _match = re.match(
                        # Note:
                        # 4 spaces after 'ERROR' in general
                        # 2 more spaces due to :meth:`.testerrors.ExceptionError.logerror()`
                        rb'^(%s - |)ERROR {4}( {2}|)(.*)$' % ISO8601_REGEX.encode("utf-8"),
                        _stdout_line,
                    )  # type: typing.Optional[typing.Match[bytes]]
                    if _match:
                        _fallbackerror(_match.group(3).decode("utf-8"))

            # Save stderr lines as well.
            for _stderr_line in _subprocess.stderr.splitlines():  # type: bytes
                if _stderr_line:
                    _fallbackerror(_stderr_line.decode("utf-8"))

            # Specific case when the file does not exist:
            # it causes a ARGUMENTS_ERROR that displays its error while the logging service is not started up yet,
            # thus we don't catch the 'No such file error'
            if _subprocess.returncode == ErrorCode.ARGUMENTS_ERROR:
                if not test_case_execution.script_path.is_file():
                    _fallbackerror(f"No such file '{test_case_execution.script_path}'")

            # Terminate the fake scenario execution.
            _fallback_errors.execution.time.setendtime()
            _exec_times_logger.tick("After execution error management")
        # From now, the scenario execution instance necessarily exists.
        assert test_case_execution.scenario_execution

        # Dispatch handlers.
        if test_case_execution.scenario_execution:
            for _error in test_case_execution.scenario_execution.errors:  # type: TestError
                HANDLERS.callhandlers(ScenarioEvent.ERROR, _error)
        HANDLERS.callhandlers(ScenarioEvent.AFTER_TEST_CASE, ScenarioEventData.TestCase(test_case_execution=test_case_execution))
        _exec_times_logger.tick("After *after-test-case* handlers")

        # Terminate the test case instance.
        _exec_times_logger.tick("Ending test case")
        test_case_execution.time.setendtime()
        CAMPAIGN_LOGGING.endtestcase(test_case_execution)

        # Feed the :attr:`.scenarioresults.SCENARIO_RESULTS` instance.
        SCENARIO_RESULTS.add(test_case_execution.scenario_execution)

        _exec_times_logger.finish()
        return ErrorCode.SUCCESS


__doc__ += """
.. py:attribute:: CAMPAIGN_RUNNER

    Main instance of :class:`CampaignRunner`.
"""
CAMPAIGN_RUNNER = CampaignRunner()  # type: CampaignRunner
