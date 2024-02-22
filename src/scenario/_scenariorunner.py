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
Scenario execution management.
"""

import sys
import time
import typing

if True:
    from ._args import Args as _ArgsImpl  # `Args` imported once for performance concerns.
    from ._enumutils import isin as _isin  # `isin()` imported once for performance concerns.
    from ._enumutils import StrEnum as _StrEnumImpl  # `StrEnum` used for inheritance.
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._logextradata import LogExtraData as _LogExtraDataImpl  # `LogExtraData` imported once for performance concerns.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
    from ._scenariodefinition import ScenarioDefinitionHelper as _ScenarioDefinitionHelperImpl  # Imported once for performance concerns.
    from ._stepdefinition import StepDefinition as _StepDefinitionImpl  # Imported once for performance concerns.
    from ._stepdefinition import StepDefinitionHelper as _StepDefinitionHelperImpl  # Imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from ._errcodes import ErrorCode as _ErrorCodeType
    from ._knownissues import KnownIssue as _KnownIssueType
    from ._path import AnyPathType as _AnyPathType
    from ._path import Path as _PathType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._stepdefinition import StepDefinition as _StepDefinitionType
    from ._stepspecifications import AnyStepDefinitionSpecificationType as _AnyStepDefinitionSpecificationType
    from ._stepuserapi import StepUserApi as _StepUserApiType
    from ._testerrors import TestError as _TestErrorType
    from ._textutils import AnyLongTextType as _AnyLongTextType


class ScenarioRunner(_LoggerImpl):
    """
    Test execution engine: runs scenarios, i.e. instances derived from the :class:`._scenariodefinition.ScenarioDefinition` class.

    Instantiated once with the :data:`SCENARIO_RUNNER` singleton.

    Implements the :meth:`main()` function for scenario executions.

    This class works with the following helper classes, with their respected purpose:

    - :class:`._scenarioargs.ScenarioArgs`: command line arguments,
    - :class:`._scenarioexecution.ScenarioExecution`: object that describes a scenario execution,
    - :class:`._scenariostack.ScenarioStack`: stack of :class:`._scenarioexecution.ScenarioExecution`,
    - :class:`._scenariologging.ScenarioLogging`: scenario execution logging,
    - :class:`._scenarioreport.ScenarioReport`: scenario report generation.
    """

    class ExecutionMode(_StrEnumImpl):
        """
        Execution mode enum.

        Tells whether the scenario runner is currently:

        - building the objects,
        - generating the documentation,
        - or executing the test.
        """
        #: The scenario runner is currently building the test objects.
        BUILD_OBJECTS = "build"
        #: The scenario runner is currently generating the test documentation.
        DOC_ONLY = "doc-only"
        #: The scenario runner is currently executing the final test script.
        EXECUTE = "execute"

    def __init__(self):  # type: (...) -> None
        """
        Sets up logging for the :class:`ScenarioRunner` class, and member variables.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, log_class=DebugClass.SCENARIO_RUNNER)
        self.setextradata(_LogExtraDataImpl.ACTION_RESULT_MARGIN, False)

    def main(self):  # type: (...) -> _ErrorCodeType
        """
        Scenario runner main function, as a member method.

        :return: Error code.
        """
        from ._errcodes import ErrorCode
        from ._loggingservice import LOGGING_SERVICE
        from ._scenarioargs import ScenarioArgs
        from ._scenarioexecution import ScenarioExecution
        from ._scenarioreport import SCENARIO_REPORT
        from ._scenarioresults import SCENARIO_RESULTS

        try:
            # Analyze program arguments, if not already set.
            if not ScenarioArgs.isset():
                ScenarioArgs.setinstance(ScenarioArgs())
                if not ScenarioArgs.getinstance().parse(sys.argv[1:]):
                    return ScenarioArgs.getinstance().error_code

            # Start log features.
            LOGGING_SERVICE.start()

            # Load requirements.
            for _req_db_file in _FAST_PATH.scenario_config.reqdbfiles():  # type: _PathType
                _FAST_PATH.main_logger.info(f"Loading requirements from '{_req_db_file}'")
                _FAST_PATH.req_db.load(_req_db_file)

            # Execute tests.
            _errors = []  # type: typing.List[ErrorCode]
            for _scenario_path in ScenarioArgs.getinstance().scenario_paths:  # type: _PathType
                self.debug("Executing '%s'...", _scenario_path)

                _res = self.executepath(_scenario_path)  # type: ErrorCode
                if _res != ErrorCode.SUCCESS:
                    # The `executepath()` and `execute()` methods don't return `ErrorCode.TEST_ERROR`.
                    # If the return code is not `ErrorCode.SUCCESS` at this point, it means this is a serious error.
                    # Stop processing right away.
                    return _res

                # Retrieve the last scenario execution.
                assert _FAST_PATH.scenario_stack.size == 0
                if not _FAST_PATH.scenario_stack.history:
                    self.error("No last scenario after execution")
                    return ErrorCode.INTERNAL_ERROR
                _scenario_execution = _FAST_PATH.scenario_stack.history[-1]  # type: ScenarioExecution

                # Manage test errors.
                if _scenario_execution.errors:
                    _errors.append(ErrorCode.TEST_ERROR)

                # Feed the `SCENARIO_RESULTS` instance.
                SCENARIO_RESULTS.add(_scenario_execution)

                # Generate scenario report if required.
                _scenario_report = ScenarioArgs.getinstance().scenario_report  # type: typing.Optional[_PathType]
                if _scenario_report:
                    try:
                        SCENARIO_REPORT.writescenarioreport(_scenario_execution.definition, _scenario_report)
                    except Exception as _err:
                        _FAST_PATH.main_logger.error(f"Error while writing '{_scenario_report}': {_err}")
                        # Note: Full traceback will be displayed in the main `except` block below.
                        raise

            # Display final results (when applicable).
            if SCENARIO_RESULTS.count > 1:
                SCENARIO_RESULTS.display()

            # Terminate log features.
            LOGGING_SERVICE.stop()

            # End test.
            return ErrorCode.worst(_errors)

        except Exception as _err:
            _FAST_PATH.main_logger.logexceptiontraceback(_err)
            return ErrorCode.fromexception(_err)

    # Scenario execution.

    @property
    def _execution_mode(self):  # type: () -> ScenarioRunner.ExecutionMode
        """
        Current execution mode.

        Depends on
        1) the scenario stack building context,
        and 2) the scenario args --doc-only option.
        """
        from ._scenarioargs import ScenarioArgs

        if _FAST_PATH.scenario_stack.building.scenario_definition:
            return ScenarioRunner.ExecutionMode.BUILD_OBJECTS
        elif isinstance(_ArgsImpl.getinstance(), ScenarioArgs):
            if ScenarioArgs.getinstance().doc_only:
                return ScenarioRunner.ExecutionMode.DOC_ONLY
            else:
                return ScenarioRunner.ExecutionMode.EXECUTE
        else:
            return ScenarioRunner.ExecutionMode.BUILD_OBJECTS

    def executepath(
            self,
            scenario_path,  # type: _AnyPathType
    ):  # type: (...) -> _ErrorCodeType
        """
        Executes a scenario from its script path.

        :param scenario_path:
            Scenario Python script path.
        :return:
            Error code, but no :attr:`._errcodes.ErrorCode.TEST_ERROR`.

        Feeds the :data:`._scenarioresults.SCENARIO_RESULTS` instance.
        """
        from ._errcodes import ErrorCode

        # Save the current time before loading the scenario script
        # and the `ScenarioDefinition` instance has been eventually created.
        _t0 = time.time()  # type: float

        # Create a test instance.
        try:
            _scenario_definition_class = _ScenarioDefinitionHelperImpl.getscenariodefinitionclassfromscript(scenario_path) \
                # type: typing.Type[_ScenarioDefinitionType]
        except ImportError as _err:
            _FAST_PATH.main_logger.logexceptiontraceback(_err)
            return ErrorCode.INPUT_MISSING_ERROR
        except SyntaxError as _err:
            _FAST_PATH.main_logger.logexceptiontraceback(_err)
            return ErrorCode.INPUT_FORMAT_ERROR
        except LookupError as _err:
            _FAST_PATH.main_logger.logexceptiontraceback(_err)
            return ErrorCode.INPUT_FORMAT_ERROR

        try:
            _scenario_definition = _scenario_definition_class()  # type: _ScenarioDefinitionType
        except Exception as _err:
            # Unexpected exception.
            _FAST_PATH.main_logger.error(f"Unexpected exception: {_err}")
            _FAST_PATH.main_logger.logexceptiontraceback(_err)
            return ErrorCode.INTERNAL_ERROR

        _err_code = self.executescenario(
            _scenario_definition,
            # Instanciation sometimes takes a while.
            # Ensure the starting time is set to when this method has actually been called.
            start_time=_t0,
        )  # type: ErrorCode

        return _err_code

    def executescenario(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
            start_time=None,  # type: float
    ):  # type: (...) -> _ErrorCodeType
        """
        Executes a scenario or subscenario.

        :param scenario_definition:
            Scenario to execute.
        :param start_time:
            Optional starting time specification.

            May be set in order to save the most accurate info on the starting time of the scenario.
        :return:
            Error code, but no :attr:`._errcodes.ErrorCode.TEST_ERROR`.
        """
        from ._errcodes import ErrorCode

        self.debug("Executing scenario %r", scenario_definition)

        # Build and begin the scenario.
        _res = self._buildscenario(scenario_definition)  # type: ErrorCode
        if _res != ErrorCode.SUCCESS:
            return _res
        assert scenario_definition.execution
        _res = self._beginscenario(scenario_definition)
        if _res != ErrorCode.SUCCESS:
            return _res
        if start_time is not None:
            # Fix the starting time when the `starting_time` parameter is set.
            scenario_definition.execution.time.start = start_time

        # Execute each step in the stack.
        scenario_definition.execution.startsteplist()
        while (not self._shouldstop()) and scenario_definition.execution.current_step_definition:
            # Execute the step.
            with self.pushindentation():
                self._execstep(scenario_definition.execution.current_step_definition)

            # Move to next step.
            if scenario_definition.execution.current_step_definition is not None:
                scenario_definition.execution.nextstep()

        # End the scenario.
        _res = self._endscenario(scenario_definition)
        if _res != ErrorCode.SUCCESS:
            return _res

        # Whether a test error occurred or not, return SUCCESS in this method.
        return ErrorCode.SUCCESS

    def _buildscenario(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> _ErrorCodeType
        """
        Builds a scenario definition.

        :param scenario_definition: :class:`._scenariodefinition.ScenarioDefinition` instance to populate with steps, actions and expected results definitions.
        :return: Error code.
        """
        from ._errcodes import ErrorCode
        from ._scenarioexecution import ScenarioExecution

        self.debug("_buildscenario(scenario_definition=%r)", scenario_definition)

        with self.pushindentation():
            # Inspect the scenario definition class to build step definitions from methods
            _ScenarioDefinitionHelperImpl(scenario_definition).buildsteps()

            # Feed the building context of the scenario stack with the scenario definition being built.
            _FAST_PATH.scenario_stack.building.pushscenariodefinition(scenario_definition)

            # Create the `ScenarioExecution` instance right now.
            # Even though we are only building objects for now,
            # this is required to make it possible to iterate over the step list (just after), and execute them in the `BUILD_OBJECTS` exection mode.
            scenario_definition.execution = ScenarioExecution(scenario_definition)

            # Start iterating over the step list.
            scenario_definition.execution.startsteplist()
            while scenario_definition.execution.current_step_definition:
                with self.pushindentation():
                    # Save *init* known issues for this step definition
                    # before executing the step and collecting other known issues registered at the definition level.
                    # These known issues shall be notified before the step is actually executed.
                    _StepDefinitionHelperImpl(scenario_definition.execution.current_step_definition).saveinitknownissues()

                    # Execute the step method in the `BUILD_OBJECTS` exection mode.
                    self._execstep(scenario_definition.execution.current_step_definition)

                # Continue iterating over the step list.
                scenario_definition.execution.nextstep()

            # Eventually remove the scenario definition reference from the building context of the scenario stack.
            _FAST_PATH.scenario_stack.building.popscenariodefinition(scenario_definition)

        return ErrorCode.SUCCESS

    def _beginscenario(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> _ErrorCodeType
        """
        Begins a scenario or subscenario execution.

        :param scenario_definition: Scenario or subscenario which execution to start.
        :return: Error code.
        """
        from ._errcodes import ErrorCode
        from ._handlers import HANDLERS
        from ._scenarioattributes import CoreScenarioAttributes
        from ._scenarioevents import ScenarioEvent, ScenarioEventData
        from ._scenariologging import SCENARIO_LOGGING

        self.debug("_beginscenario(scenario_definition=%r)", scenario_definition)

        with self.pushindentation():
            # Scenario execution stack management:
            # - Note: The scenario execution instance has already been created in `_buildscenario()`.
            assert scenario_definition.execution
            # - Before pushing the scenario execution to the stack, store the subscenario reference in the current action / expected result when applicable.
            if _FAST_PATH.scenario_stack.current_action_result_execution:
                _FAST_PATH.scenario_stack.current_action_result_execution.subscenarios.append(scenario_definition.execution)
            # - Eventually push the scenario execution to the execution stack.
            _FAST_PATH.scenario_stack.pushscenarioexecution(scenario_definition.execution)

            # Test intro.
            SCENARIO_LOGGING.beginscenario(scenario_definition)

            # Check and display that the main scenario attributes.
            # (main scenario only)
            if _FAST_PATH.scenario_stack.ismainscenario(scenario_definition):
                SCENARIO_LOGGING.beginheadinginfo()

                # Display scenario attributes.
                for _attribute_name in scenario_definition.getattributenames():  # type: str
                    # Skip empty core attributes.
                    if _isin(_attribute_name, CoreScenarioAttributes) and (not scenario_definition.getattribute(_attribute_name)):
                        continue
                    SCENARIO_LOGGING.attribute(_attribute_name, scenario_definition.getattribute(_attribute_name))

                # Check expected scenario attributes.
                _expected_attribute_names = _FAST_PATH.scenario_config.expectedscenarioattributes()  # type: typing.List[str]
                self.debug("Expected attributes: %r", _expected_attribute_names)
                for _expected_attribute_name in _expected_attribute_names:  # type: str
                    if _expected_attribute_name not in scenario_definition.getattributenames():
                        _FAST_PATH.main_logger.error(f"Missing test attribute {_expected_attribute_name}")
                        self.popindentation()
                        return ErrorCode.INPUT_FORMAT_ERROR

                # Requirement verifications.
                SCENARIO_LOGGING.reqcoverage(scenario_definition)

                SCENARIO_LOGGING.endheadinginfo()

            # Start execution time.
            assert scenario_definition.execution is not None
            scenario_definition.execution.time.setstarttime()

            # Execute *before test* handlers.
            HANDLERS.callhandlers(ScenarioEvent.BEFORE_TEST, ScenarioEventData.Scenario(scenario_definition=scenario_definition))

            # Notify every known issues registered at the definition level.
            self._notifyknownissuedefinitions(scenario_definition)

        return ErrorCode.SUCCESS

    def _endscenario(
            self,
            scenario_definition,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> _ErrorCodeType
        """
        Ends a scenario or subscenario execution.

        :param scenario_definition: Scenario or subscenario which execution to end.
        :return: Error code.
        """
        from ._errcodes import ErrorCode
        from ._handlers import HANDLERS
        from ._scenarioevents import ScenarioEvent, ScenarioEventData
        from ._scenariologging import SCENARIO_LOGGING

        self.debug("_endscenario(scenario_definition=%r)", scenario_definition)

        with self.pushindentation():
            assert _FAST_PATH.scenario_stack.iscurrentscenario(scenario_definition)
            assert scenario_definition.execution

            # Known issues:
            # - Finish iterating over the steps in order to notify each known issue defined at the definition level.
            while scenario_definition.execution.current_step_definition:
                self._notifyknownissuedefinitions(scenario_definition.execution.current_step_definition)
                scenario_definition.execution.nextstep()
            # - Check that all known issues registered at the definition level have been notified.
            self._notifyknownissuedefinitions(scenario_definition)

            # Execute *after test* handlers (whether the test is SUCCESS or not).
            HANDLERS.callhandlers(ScenarioEvent.AFTER_TEST, ScenarioEventData.Scenario(scenario_definition=scenario_definition))

            # End execution time.
            scenario_definition.execution.time.setendtime()

            # Test outro.
            SCENARIO_LOGGING.endscenario(scenario_definition)

            # Pop the scenario from the stack.
            _FAST_PATH.scenario_stack.popscenarioexecution()

            if _FAST_PATH.scenario_stack.size > 0:
                # When errors occurred, and this in not the main scenario,
                # raise the last error in order to break the execution of the parent scenario.
                if scenario_definition.execution.errors:
                    raise scenario_definition.execution.errors[-1]

            if _FAST_PATH.scenario_stack.size == 0:
                SCENARIO_LOGGING.displaystatistics(scenario_definition.execution)

        return ErrorCode.SUCCESS

    def _execstep(
            self,
            step_definition,  # type: _StepDefinitionType
    ):  # type: (...) -> None
        """
        Executes the step.

        :param step_definition: Step definition to execute.
        """
        from ._handlers import HANDLERS
        from ._scenarioevents import ScenarioEvent, ScenarioEventData
        from ._scenariologging import SCENARIO_LOGGING
        from ._stepexecution import StepExecution
        from ._stepsection import StepSectionDescription
        from ._testerrors import ExceptionError, TestError

        self.debug("Beginning of %r", step_definition)

        if isinstance(step_definition, StepSectionDescription):
            if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                SCENARIO_LOGGING.stepsectiondescription(step_definition)
        else:
            # Step execution number, starting from 1.
            # Sum up step executions already known for the given scenario.
            _step_number = 1  # type: int
            for _step_definition in step_definition.scenario.steps:  # type: _StepDefinitionType
                # Skip step sections.
                if isinstance(_step_definition, StepSectionDescription):
                    continue
                _step_number += len(_step_definition.executions)

            # Execute *before step* handlers.
            if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                HANDLERS.callhandlers(ScenarioEvent.BEFORE_STEP, ScenarioEventData.Step(step_definition=step_definition))
                if self._shouldstop() or (not _FAST_PATH.scenario_stack.current_step_definition):
                    self.debug("Execution of %r aborted after *before step* handlers", step_definition)
                    return

            # Create the step execution instance (will be dropped in DOC_ONLY mode in the end).
            # Start time by the way.
            if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                step_definition.executions.append(StepExecution(step_definition, _step_number))

            # Display the step description.
            if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                SCENARIO_LOGGING.stepdescription(step_definition)

            # Notify *init* known issues saved for this step before executing it.
            self._notifyknownissuedefinitions(step_definition, _StepDefinitionHelperImpl(step_definition).getinitknownissues())

            # Method execution.
            self.debug("Executing %r in %s mode", step_definition, self._execution_mode.name)
            with self.pushindentation():
                try:
                    step_definition.step()
                except GotoException:
                    # This exception was raised to stop the execution in the step,
                    # but is not representative of an error.
                    pass
                except TestError as _error:
                    # Test error propagation as is.
                    self.onerror(_error)
                except Exception as _exception:
                    # An exception occurred during the test.
                    self.onerror(ExceptionError(exception=_exception))
                except KeyboardInterrupt as _interrupt:
                    # CTRL+C.
                    self.onerror(ExceptionError(exception=_interrupt))
                finally:
                    # Ensure the current action/result (if any) is terminated after the step execution.
                    if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                        self._endcurrentactionresult()

            # Check that all known issues registered at the definition level have been notified.
            self._notifyknownissuedefinitions(step_definition)

            if self._execution_mode == ScenarioRunner.ExecutionMode.DOC_ONLY:
                # Drop the step execution instance.
                del step_definition.executions[-1]
            elif self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE:
                # End time.
                step_definition.executions[-1].time.setendtime()

            # Execute *after step* handlers.
            if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                HANDLERS.callhandlers(ScenarioEvent.AFTER_STEP, ScenarioEventData.Step(step_definition=step_definition))

        self.debug("End of %r", step_definition)

        # Delay between steps.
        if self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE:
            _delay = _FAST_PATH.scenario_config.delaybetweensteps()  # type: float
            if self.doexecute() and (_delay > 0.0):
                time.sleep(_delay)

    def onstepdescription(
            self,
            description,  # type: str
    ):  # type: (...) -> None
        """
        Call redirection from :meth:`._stepuserapi.StepUserApi.STEP()`.

        :param description: Step description.
        """
        self.debug("onstepdescription(description=%r)", description)

        if self._execution_mode == ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            # Build objects.
            if _FAST_PATH.scenario_stack.building.step_definition:
                _FAST_PATH.scenario_stack.building.step_definition.description = description
            else:
                _FAST_PATH.scenario_stack.raisecontexterror("No building step definition")

    def _notifyknownissuedefinitions(
            self,
            step_user_api,  # type: _StepUserApiType
            known_issues=None,  # type: typing.Sequence[_KnownIssueType]
    ):  # type: (...) -> None
        """
        Notifies the known issues declared at the definition level for the given scenario or step definition.

        :param step_user_api:
            Scenario or step definition to process known issues for.
        :param known_issues:
            Specific known issue list to process.
            Defaults to :attr:`._stepuserapi.StepUserApi.known_issues` when not set.
        """
        if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            if known_issues is None:
                known_issues = step_user_api.known_issues

            for _known_issue in known_issues:  # type: _KnownIssueType
                self.debug("Notifying known issue from %r", step_user_api)
                self.onerror(_known_issue)

    def onactionresult(
            self,
            action_result_type,  # type: _ActionResultDefinitionType.Type
            description,  # type: _AnyLongTextType
    ):  # type: (...) -> None
        """
        Call redirection from :meth:`._stepuserapi.StepUserApi.ACTION()` or :meth:`._stepuserapi.StepUserApi.RESULT()`.

        :param action_result_type: ACTION or RESULT.
        :param description: Action or expected result description.
        """
        from ._actionresultdefinition import ActionResultDefinition
        from ._actionresultexecution import ActionResultExecution
        from ._scenariologging import SCENARIO_LOGGING
        from ._stepexecution import StepExecutionHelper
        from ._textutils import anylongtext2str

        self.debug("onactionresult(action_result_type=%s, description=%r)", action_result_type, description)

        if self._execution_mode == ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            # Build objects.
            if not _FAST_PATH.scenario_stack.building.step_definition:
                _FAST_PATH.scenario_stack.raisecontexterror("No building step definition")

            _FAST_PATH.scenario_stack.building.step_definition.addactionresult(
                ActionResultDefinition(
                    type=action_result_type,
                    description=description,
                ),
            )

        else:
            if not _FAST_PATH.scenario_stack.current_step_execution:
                _FAST_PATH.scenario_stack.raisecontexterror("No current step definition")

            # Terminate the previous action/result, if any.
            self._endcurrentactionresult()

            # Switch to this action/result.
            _step_execution_helper = StepExecutionHelper(_FAST_PATH.scenario_stack.current_step_execution)  # type: StepExecutionHelper
            _action_result_definition = _step_execution_helper.getnextactionresultdefinition()  # type: ActionResultDefinition
            if (_action_result_definition.type != action_result_type) or (_action_result_definition.description != anylongtext2str(description)):
                _FAST_PATH.scenario_stack.raisecontexterror(f"Bad {_action_result_definition}, {action_result_type} {description!r} expected.")

            # Create the action/result execution instance (in EXECUTE mode only).
            if self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE:
                _action_result_definition.executions.append(ActionResultExecution(_action_result_definition))

            # Display.
            SCENARIO_LOGGING.actionresult(_action_result_definition)

    def _endcurrentactionresult(self):  # type: (...) -> None
        """
        Ends the current action or expected result section.
        """
        if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            if (
                _FAST_PATH.scenario_stack.current_step_execution
                and _FAST_PATH.scenario_stack.current_action_result_definition
                and _FAST_PATH.scenario_stack.current_action_result_execution
            ):
                self.debug(
                    "_endcurrentactionresult(): type=%s, description=%r",
                    _FAST_PATH.scenario_stack.current_action_result_definition.type, _FAST_PATH.scenario_stack.current_action_result_definition.description,
                )

                if self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE:
                    _FAST_PATH.scenario_stack.current_action_result_execution.time.setendtime()

                _FAST_PATH.scenario_stack.current_step_execution.current_action_result_definition = None

    def onevidence(
            self,
            evidence,  # type: str
    ):  # type: (...) -> None
        """
        Call redirection from :meth:`._stepuserapi.StepUserApi.evidence()`.

        :param evidence: Evidence text.
        """
        from ._scenariologging import SCENARIO_LOGGING

        self.debug("onevidence(evidence=%r)", evidence)

        if _FAST_PATH.scenario_stack.current_action_result_execution:
            # Save the execution data.
            _FAST_PATH.scenario_stack.current_action_result_execution.evidence.append(evidence)
            # Console display.
            SCENARIO_LOGGING.evidence(evidence)
        else:
            _FAST_PATH.scenario_stack.raisecontexterror("No current action / expected result execution")

    def doexecute(self):  # type: (...) -> bool
        """
        Tells whether the test script shall be executed.

        :return: ``True`` when the test script shall be executed.
        """
        return self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE

    def onerror(
            self,
            error,  # type: _TestErrorType
            originator=None,  # type: _StepUserApiType
    ):  # type: (...) -> None
        """
        Called when an error occurs.

        :param error: Error that occurred.
        :param originator: Scenario or step definition that made the call to :meth:`onerror()`, set in :meth:.stepuserapi.StepUserApi.knownissue()`..
        """
        from ._actionresultexecution import ActionResultExecution
        from ._handlers import HANDLERS
        from ._knownissues import KnownIssue
        from ._scenarioevents import ScenarioEvent, ScenarioEventData
        from ._scenarioexecution import ScenarioExecution
        from ._scenariologging import SCENARIO_LOGGING
        from ._stepexecution import StepExecution

        self.debug("onerror(error=%r, originator=%r)", error, originator)

        # Return right away if the error is ignored.
        if error.isignored():
            self.debug(f"Error %r ignored", error)
            return

        if self._execution_mode == ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            # Build objects.
            if isinstance(error, KnownIssue):
                if originator:
                    _FAST_PATH.scenario_stack.building.fromoriginator(originator).known_issues.append(error)
                else:
                    _FAST_PATH.scenario_stack.raisecontexterror("Originator missing for known issue while building objects")
            else:
                # Cannot register the error while building objects.
                # Just raise the error.
                raise error
        else:
            # Discard duplicate `KnownIssue` instances created on consecutive `StepDefinition.step()` calls.
            # Stick with the first instance registered at definition level.
            if isinstance(error, KnownIssue) and isinstance(originator, _StepDefinitionImpl):
                for _known_issue in originator.known_issues:  # type: KnownIssue
                    if _known_issue == error:
                        self.debug(f"%r: discarding %r in favor of %r", originator, error, _known_issue)
                        error = _known_issue
                        break

            # Do not process errors twice.
            # Note: This filtering particularly applies to known issues possibly reprocessed from `_notifyknownissuedefinitions()`.
            if _FAST_PATH.scenario_stack.current_scenario_execution:
                if (
                    (error in _FAST_PATH.scenario_stack.current_scenario_execution.errors)
                    or (error in _FAST_PATH.scenario_stack.current_scenario_execution.warnings)
                ):
                    self.debug(f"Error %r already processed", error)
                    return

            # Display the error.
            if not self._shouldstop():
                SCENARIO_LOGGING.error(error)

            # Memorize the error in the current execution context.
            def _store_error(
                    obj,  # type: typing.Optional[typing.Union[ScenarioExecution, StepExecution, ActionResultExecution]]
            ):  # type: (...) -> bool
                # Check the current object is valid.
                if obj is None:
                    return False
                # Determine the candidate list to store the error into.
                _list = obj.warnings if error.iswarning() else obj.errors  # type: typing.List[_TestErrorType]
                # Do not store known issues twice (in the owner execution contexts among others).
                if isinstance(error, KnownIssue) and (error in _list):
                    return False
                # Store the error in the candidate list.
                _list.append(error)
                self.debug(f"%r saved with %r => %d items", error, obj, len(_list))
                return True
            _store_error(_FAST_PATH.scenario_stack.current_scenario_execution)
            _store_error(_FAST_PATH.scenario_stack.current_step_execution)
            # When the known issue has been registered at the definition level,
            # do not push it to a current action/expected result execution.
            if _FAST_PATH.scenario_stack.current_step_definition and (error in _FAST_PATH.scenario_stack.current_step_definition.known_issues):
                self.debug(f"%r registered at definition level => not saved with %r", error, _FAST_PATH.scenario_stack.current_action_result_execution)
            else:
                _store_error(_FAST_PATH.scenario_stack.current_action_result_execution)

            # Call error handlers (if `error` is actually an error).
            if error.iserror():
                HANDLERS.callhandlers(ScenarioEvent.ERROR, ScenarioEventData.Error(error=error))

    def _shouldstop(self):  # type: (...) -> bool
        """
        Tells whether the scenario execution should stop.

        :return: ``True`` when the scenario execution should stop, ``False`` when the scenario execution should continue on.
        """
        from ._knownissues import KnownIssue

        if _FAST_PATH.scenario_stack.current_scenario_execution and _FAST_PATH.scenario_stack.current_scenario_execution.errors:
            # Errors occurred.
            # Check whether these errors are real errors, or just known issues considered as errors.
            _real_errors = 0  # type: int
            for _error in _FAST_PATH.scenario_stack.current_scenario_execution.errors:  # type: _TestErrorType
                if not isinstance(_error, KnownIssue):
                    _real_errors += 1
            if not _real_errors:
                # No real error, keep going.
                return False

            # Real errors occurred.
            # Let's stop by default, unless a configuration says not to.

            # First check whether a local configuration is set for the scenario.
            if _FAST_PATH.scenario_stack.current_scenario_definition and _FAST_PATH.scenario_stack.current_scenario_definition.continue_on_error:
                return False

            # Check for a global configuration.
            if _FAST_PATH.scenario_config.continueonerror():
                return False

            # Ok, let's stop then.
            return True

        # No error, keep going.
        return False

    def goto(
            self,
            to_step_specification,  # type: _AnyStepDefinitionSpecificationType
    ):  # type: (...) -> None
        """
        Call redirection from :meth:`._stepuserapi.StepUserApi.goto()`.

        :param to_step_specification: Specification of the next step to execute.
        """
        from ._stepspecifications import StepDefinitionSpecification

        self.debug("Jumping to step %s", to_step_specification)

        # Resolve the *to-step* specification.
        if not isinstance(to_step_specification, StepDefinitionSpecification):
            to_step_specification = StepDefinitionSpecification(to_step_specification)
        _next_step_definition = to_step_specification.expect()  # type: _StepDefinitionType

        # Set it as the next step for execution, then break the current step execution by raising a `GotoException`.
        if _FAST_PATH.scenario_stack.current_scenario_execution:
            _FAST_PATH.scenario_stack.current_scenario_execution.setnextstep(_next_step_definition)
            raise GotoException()
        else:
            _FAST_PATH.scenario_stack.raisecontexterror("No current scenario definition or execution")


class GotoException(Exception):
    """
    Breaks execution in a step method when :meth:`._stepuserapi.StepUserApi.goto()` is called.
    """


#: Main instance of :class:`ScenarioRunner`.
SCENARIO_RUNNER = ScenarioRunner()  # type: ScenarioRunner
