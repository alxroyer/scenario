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
Campaign execution management.
"""

import re
import sys
import time
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionImpl  # `ScenarioDefinition` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._campaignexecution import CampaignExecution as _CampaignExecutionType
    from ._campaignexecution import TestCaseExecution as _TestCaseExecutionType
    from ._campaignexecution import TestSuiteExecution as _TestSuiteExecutionType
    from ._errcodes import ErrorCode as _ErrorCodeType
    from ._path import AnyPathType as _AnyPathType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


class CampaignRunner(_LoggerImpl):
    """
    Campaign execution engine: runs test scenarios from input files.

    Instantiated once with the :data:`CAMPAIGN_RUNNER` singleton.

    This class works with the following helper classes, with their respected purpose:

    - :class:`._campaignargs.CampaignArgs`: command line arguments,
    - :class:`._campaignexecution.CampaignExecution`: object that describes a campaign execution,
    - :class:`._campaignlogging.CampaignLogging`: campaign execution logging,
    - :class:`._campaignreport.CampaignReport`: campaign report generation,
    - :class:`._reqdb.ReqDatabase`: requirement database export.
    """

    def __init__(self):  # type: (...) -> None
        """
        Configures logging for the :class:`CampaignRunner` class.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, log_class=DebugClass.CAMPAIGN_RUNNER)

    def main(self):  # type: (...) -> _ErrorCodeType
        """
        Campaign runner main function, as a member method.

        :return: Error code.
        """
        from ._campaignargs import CampaignArgs
        from ._campaignexecution import CampaignExecution
        from ._campaignlogging import CAMPAIGN_LOGGING
        from ._campaignreport import CAMPAIGN_REPORT
        from ._datetimeutils import toiso8601
        from ._errcodes import ErrorCode
        from ._handlers import HANDLERS
        from ._loggermain import MAIN_LOGGER
        from ._loggingservice import LOGGING_SERVICE
        from ._path import Path
        from ._reqdb import REQ_DB
        from ._reqtraceability import REQ_TRACEABILITY
        from ._scenarioevents import ScenarioEvent, ScenarioEventData
        from ._scenarioresults import SCENARIO_RESULTS

        try:
            # Analyze program arguments, if not already set.
            if not CampaignArgs.isset():
                CampaignArgs.setinstance(CampaignArgs())
                if not CampaignArgs.getinstance().parse(sys.argv[1:]):
                    return CampaignArgs.getinstance().error_code
            _test_suite_files = _FAST_PATH.scenario_config.testsuitefiles()  # type: typing.Sequence[Path]
            if not _test_suite_files:
                MAIN_LOGGER.error("No test suite files")
                return ErrorCode.INPUT_MISSING_ERROR

            # Create the date/time output directory (if required).
            if CampaignArgs.getinstance().create_dt_subdir:
                _outdir_basename = toiso8601(time.time())[:len("XXXX-XX-XXTXX:XX:XX")].replace(":", "-").replace("T", "_")  # type: str
                _outdir = CampaignArgs.getinstance().outdir / _outdir_basename  # type: Path
            else:
                _outdir = CampaignArgs.getinstance().outdir
            _outdir.mkdir(parents=True, exist_ok=True)

            # Start log features.
            LOGGING_SERVICE.start()

            # Load requirements.
            for _req_db_file in _FAST_PATH.scenario_config.reqdbfiles():  # type: Path
                MAIN_LOGGER.info(f"Loading requirements from '{_req_db_file}'")
                REQ_DB.load(_req_db_file)

            _campaign_execution = CampaignExecution(_outdir)  # type: CampaignExecution

            # *before-campaign* handlers.
            HANDLERS.callhandlers(ScenarioEvent.BEFORE_CAMPAIGN, ScenarioEventData.Campaign(campaign_execution=_campaign_execution))

            # Start logging.
            CAMPAIGN_LOGGING.begincampaign(_campaign_execution)

            # Execute the campaign.
            _campaign_execution.time.setstarttime()
            for _test_suite_path in _test_suite_files:  # type: Path
                self._exectestsuitefile(_campaign_execution, _test_suite_path)
            _campaign_execution.time.setendtime()

            # Dump requirement files (only when there are requirements).
            if REQ_DB.getallreqs():
                # Requirement database.
                REQ_DB.dump(_campaign_execution.req_db_path)
                # Downstream & upstream traceability reports.
                REQ_TRACEABILITY.loaddatafromcampaignresults(
                    _campaign_execution,
                    log_info=False,  # Don't log info messages.
                )
                REQ_TRACEABILITY.writedownstream(
                    _campaign_execution.downstream_traceability_path,
                    log_info=False,  # Don't log info messages.
                    allow_results=True,  # Save test results in traceability reports.
                )
                REQ_TRACEABILITY.writeupstream(
                    _campaign_execution.upstream_traceability_path,
                    log_info=False,  # Don't log info messages.
                )

            # Eventually write the JUnit campaign report (depends on requirement files generated before).
            try:
                CAMPAIGN_REPORT.writecampaignreport(_campaign_execution, _campaign_execution.campaign_report_path)
            except Exception as _err:
                MAIN_LOGGER.error(f"Error while writing '{_campaign_execution.campaign_report_path}': {_err}")
                MAIN_LOGGER.logexceptiontraceback(_err)
                return ErrorCode.fromexception(_err)

            # Final logging (after reports generation).
            CAMPAIGN_LOGGING.endcampaign(_campaign_execution)
            SCENARIO_RESULTS.display()

            # *after-campaign* handlers.
            HANDLERS.callhandlers(ScenarioEvent.AFTER_CAMPAIGN, ScenarioEventData.Campaign(campaign_execution=_campaign_execution))

            # Terminate log features.
            LOGGING_SERVICE.stop()

            return ErrorCode.SUCCESS

        except Exception as _err:
            MAIN_LOGGER.logexceptiontraceback(_err)
            return ErrorCode.fromexception(_err)

    def _exectestsuitefile(
            self,
            campaign_execution,  # type: _CampaignExecutionType
            test_suite_path,  # type: _AnyPathType
    ):  # type: (...) -> None
        """
        Executes a test suite file.

        :param campaign_execution: :class:`._campaignexecution.CampaignExecution` object to store results into.
        :param test_suite_path: Test suite file to execute.
        :raise: Exception when something worse than test errors occured.
        """
        from ._campaignexecution import TestSuiteExecution

        _test_suite_execution = TestSuiteExecution(campaign_execution, test_suite_path)  # type: TestSuiteExecution
        campaign_execution.test_suite_executions.append(_test_suite_execution)
        self._exectestsuite(_test_suite_execution)

    def _exectestsuite(
            self,
            test_suite_execution,  # type: _TestSuiteExecutionType
    ):  # type: (...) -> None
        """
        Executes a test suite.

        :param test_suite_execution: Test suite to execute.
        :raise: Exception when something worse than test errors occured.
        """
        from ._campaignexecution import TestCaseExecution
        from ._campaignlogging import CAMPAIGN_LOGGING
        from ._handlers import HANDLERS
        from ._path import Path
        from ._scenarioevents import ScenarioEvent, ScenarioEventData

        HANDLERS.callhandlers(ScenarioEvent.BEFORE_TEST_SUITE, ScenarioEventData.TestSuite(test_suite_execution=test_suite_execution))

        CAMPAIGN_LOGGING.begintestsuite(test_suite_execution)
        test_suite_execution.time.setstarttime()

        try:
            test_suite_execution.test_suite_file.read()

            for _test_script_path in test_suite_execution.test_suite_file.script_paths:  # type: Path
                _test_case_execution = TestCaseExecution(test_suite_execution, _test_script_path)  # type: TestCaseExecution
                test_suite_execution.test_case_executions.append(_test_case_execution)

                self._exectestcase(_test_case_execution)

        finally:
            test_suite_execution.time.setendtime()
            CAMPAIGN_LOGGING.endtestsuite(test_suite_execution)

            HANDLERS.callhandlers(ScenarioEvent.AFTER_TEST_SUITE, ScenarioEventData.TestSuite(test_suite_execution=test_suite_execution))

    def _exectestcase(
            self,
            test_case_execution,  # type: _TestCaseExecutionType
    ):  # type: (...) -> None
        """
        Executes a test case.

        :param test_case_execution: Test case to execute.
        :raise: Exception when something worse than test errors occured.
        """
        from ._campaignargs import CampaignArgs
        from ._campaignlogging import CAMPAIGN_LOGGING
        from ._confignode import ConfigNode
        from ._datetimeutils import ISO8601_REGEX
        from ._errcodes import ErrorCode
        from ._handlers import HANDLERS
        from ._path import Path
        from ._scenarioevents import ScenarioEvent, ScenarioEventData
        from ._scenarioexecution import ScenarioExecution
        from ._scenarioresults import SCENARIO_RESULTS
        from ._subprocess import SubProcess
        from ._testerrors import TestError

        HANDLERS.callhandlers(ScenarioEvent.BEFORE_TEST_CASE, ScenarioEventData.TestCase(test_case_execution=test_case_execution))

        CAMPAIGN_LOGGING.begintestcase(test_case_execution)
        test_case_execution.time.setstarttime()

        try:
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

            test_case_execution.report.path = _mkoutpath(_FAST_PATH.scenario_config.scenarioreportsuffix())
            test_case_execution.log.path = _mkoutpath(".log")

            # Prepare the command line.
            _subprocess = SubProcess(sys.executable, _FAST_PATH.scenario_config.runnerscriptpath())  # type: SubProcess
            # Report configuration files and single configuration values from campaign to scenario execution.
            for _config_path in CampaignArgs.getinstance().config_paths:  # type: Path
                _subprocess.addargs("--config-file", _config_path)
            for _config_name in CampaignArgs.getinstance().config_values:  # type: str
                _subprocess.addargs("--config-value", _config_name, CampaignArgs.getinstance().config_values[_config_name])
            # Report common execution options from campaign to scenario execution.
            CampaignArgs.reportexecargs(CampaignArgs.getinstance(), _subprocess)
            # --scenario-report option.
            _subprocess.addargs("--scenario-report", test_case_execution.report.path)
            # Log outfile specification.
            _subprocess.addargs("--config-value", str(_FAST_PATH.scenario_config.Key.LOG_FILE), test_case_execution.log.path)
            # No log console specification.
            _subprocess.addargs("--config-value", str(_FAST_PATH.scenario_config.Key.LOG_CONSOLE), "0")
            # Log date/time option propagation.
            _log_datetime_config = _FAST_PATH.config_db.getnode(_FAST_PATH.scenario_config.Key.LOG_DATETIME)  # type: typing.Optional[ConfigNode]
            if _log_datetime_config:
                _subprocess.addargs("--config-value", str(_FAST_PATH.scenario_config.Key.LOG_DATETIME), _log_datetime_config.cast(type=str))
            # Script path.
            _subprocess.addargs(test_case_execution.script_path)

            # In case no execution data is available in the end,
            # create `ScenarioDefinition` and `ScenarioExecution` instances from scratch in order to save error details.
            _fallback_errors = _ScenarioDefinitionImpl()  # type: _ScenarioDefinitionType
            _fallback_errors.name = test_case_execution.name
            _fallback_errors.execution = ScenarioExecution(_fallback_errors)
            _fallback_errors.execution.time.setstarttime()

            def _fallbackerror(
                    error_message,  # type: str
                    *,
                    extend_last_line=False,  # type: bool
            ):  # type: (...) -> None
                assert _fallback_errors.execution
                if extend_last_line and _fallback_errors.execution.errors:
                    _fallback_errors.execution.errors[-1].message += f"\n{error_message}"
                else:
                    _fallback_errors.execution.errors.append(TestError(error_message))

            # Execute the scenario.
            _subprocess.setlogger(self).run(timeout=_FAST_PATH.scenario_config.scenariotimeout())
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

            # Read the log outfile.
            if test_case_execution.log.path.is_file():
                self.debug("Reading '%s'", test_case_execution.log.path)
                try:
                    test_case_execution.log.read()
                except Exception as _err:
                    # Don't bother with errors, just debug and keep going on.
                    self.debug("Error while reading %s log file: %s", test_case_execution.name, _err)
            else:
                self.debug("No such file '%s'", test_case_execution.log.path)

            # Read the scenario report outfile.
            if test_case_execution.report.path.is_file():
                self.debug("Reading '%s'", test_case_execution.report.path)
                try:
                    test_case_execution.report.read()
                except Exception as _err:
                    # Don't bother with errors, just debug and keep going on.
                    self.debug("Error while reading %s scenario report: %s", test_case_execution.name, _err)
            else:
                self.debug("No such file '%s'", test_case_execution.report.path)

            # Fix the scenario definition and execution instances, if not successfully read from the scenario report above.
            if not test_case_execution.scenario_execution:
                self.debug("Using fallback scenario instances")
                test_case_execution.report.content = _fallback_errors

                # Read error lines from log output.
                self.debug("Reading error lines from log output")
                if test_case_execution.log.content:
                    _last_line_index = -1  # type: int
                    for _line_index, _stdout_line in enumerate(test_case_execution.log.content.splitlines()):  # type: int, bytes
                        _match = re.match(
                            # Note:
                            # 4 spaces after 'ERROR' in general.
                            # Possibly 2 more spaces due to `ExceptionError.logerror()`.
                            rb'^(%s - |)ERROR {4}( {2}|)(.*)$' % ISO8601_REGEX.encode("utf-8"),
                            _stdout_line,
                        )  # type: typing.Optional[typing.Match[bytes]]
                        if _match:
                            self.debug("  %r (_line_index=%d, _last_line_index=%d)", _match.group(3), _line_index, _last_line_index)
                            _fallbackerror(
                                _match.group(3).decode("utf-8"),
                                extend_last_line=(_last_line_index >= 0) and (_line_index == _last_line_index + 1),
                            )
                            _last_line_index = _line_index

                # Stdout should normally be empty.
                # If any, save it as an error.
                self.debug("Checking stdout: %r", _subprocess.stdout)
                if _subprocess.stdout:
                    _fallbackerror(_subprocess.stdout.decode("utf-8"))

                # Save stderr as well.
                self.debug("Checking stderr: %r", _subprocess.stderr)
                if _subprocess.stderr:
                    _fallbackerror(_subprocess.stderr.decode("utf-8"))

                # Specific case when the file does not exist:
                # it causes a ARGUMENTS_ERROR that displays its error while the logging service is not started up yet,
                # thus we don't catch the 'No such file error'
                if _subprocess.returncode == ErrorCode.ARGUMENTS_ERROR:
                    if not test_case_execution.script_path.is_file():
                        _fallbackerror(f"No such file '{test_case_execution.script_path}'")

                # Terminate the fake scenario execution.
                _fallback_errors.execution.time.setendtime()
            # From now, the scenario execution instance necessarily exists.
            assert test_case_execution.scenario_execution

        finally:
            # Terminate the test case instance.
            test_case_execution.time.setendtime()
            CAMPAIGN_LOGGING.endtestcase(test_case_execution)

            # Dispatch handlers.
            if test_case_execution.scenario_execution is not None:
                for _error in test_case_execution.scenario_execution.errors:  # type: TestError
                    HANDLERS.callhandlers(ScenarioEvent.ERROR, _error)
            HANDLERS.callhandlers(ScenarioEvent.AFTER_TEST_CASE, ScenarioEventData.TestCase(test_case_execution=test_case_execution))

            # Feed the `SCENARIO_RESULTS` instance.
            if test_case_execution.scenario_execution is not None:
                SCENARIO_RESULTS.add(test_case_execution.scenario_execution)


#: Main instance of :class:`CampaignRunner`.
CAMPAIGN_RUNNER = CampaignRunner()  # type: CampaignRunner
