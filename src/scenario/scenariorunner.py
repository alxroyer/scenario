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
Scenario execution management.
"""

import logging
import sys
import time
import typing

# `ActionResultDefinition` used in method signatures.
from .actionresultdefinition import ActionResultDefinition
# `StrEnum` used for inheritance.
from .enumutils import StrEnum
# `ErrorCode` used in method signatures.
from .errcodes import ErrorCode
# `CodeLocation` used in method signatures.
from .locations import CodeLocation
# `Logger` used for inheritance.
from .logger import Logger
# `ScenarioDefinition` used in method signatures.
from .scenariodefinition import ScenarioDefinition
# `StepDefinition` used in method signatures.
from .stepdefinition import StepDefinition
# `StepUserApi` used in method signatures.
from .stepuserapi import StepUserApi
# `TestError` used in method signatures.
from .testerrors import TestError

if typing.TYPE_CHECKING:
    # `StepSpecificationType` used in method signatures.
    # Type declared for type checking only.
    from .stepdefinition import StepSpecificationType
    # `AnyPathType` used in method signatures.
    # Type declared for type checking only.
    from .path import AnyPathType


class ScenarioRunner(Logger):
    """
    Test execution engine: runs scenarios, i.e. instances derived from the :class:`.scenariodefinition.ScenarioDefinition` class.

    Only one instance, accessible through the :attr:`SCENARIO_RUNNER` singleton.

    Implements the :meth:`main()` function for scenario executions.

    This class works with the following helper classes, with their respected purpose:

    - :class:`.scenarioargs.ScenarioArgs`: command line arguments,
    - :class:`.scenarioexecution.ScenarioExecution`: object that describes a scenario execution,
    - :class:`.scenariostack.ScenarioStack`: stack of :class:`.scenarioexecution.ScenarioExecution`,
    - :class:`.scenariologging.ScenarioLogging`: scenario execution logging,
    - :class:`.scenarioreport.ScenarioReport`: scenario report generation.
    """

    class ExecutionMode(StrEnum):
        """
        Execution mode enumerate.

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
        from .debug import DebugClass
        from .logextradata import LogExtraData

        Logger.__init__(self, log_class=DebugClass.SCENARIO_RUNNER)
        self.setextraflag(LogExtraData.ACTION_RESULT_MARGIN, False)

    def main(self):  # type: (...) -> ErrorCode
        """
        Scenario runner main function, as a member method.

        :return: Error code from the :class:`.errcodes.ErrorCode` enumerate.
        """
        from .loggermain import MAIN_LOGGER
        from .loggingservice import LOGGING_SERVICE
        from .path import Path
        from .scenarioargs import ScenarioArgs
        from .scenarioexecution import ScenarioExecution
        from .scenarioreport import SCENARIO_REPORT
        from .scenarioresults import SCENARIO_RESULTS
        from .scenariostack import SCENARIO_STACK
        from .testerrors import ExceptionError

        try:
            # Analyze program arguments, if not already set.
            if not ScenarioArgs.isset():
                # Create a first ScenarioArgs instance.
                ScenarioArgs.setinstance(ScenarioArgs())
                if not ScenarioArgs.getinstance().parse(sys.argv[1:]):
                    return ScenarioArgs.getinstance().error_code

            # Start log features.
            LOGGING_SERVICE.start()

            _errors = []  # type: typing.List[ErrorCode]
            for _scenario_path in ScenarioArgs.getinstance().scenario_paths:  # type: Path
                self.debug("Executing '%s'..." % _scenario_path)

                _res = self.executepath(_scenario_path)  # type: ErrorCode
                if _res != ErrorCode.SUCCESS:
                    # The :meth:`executepath()` and :meth:`execute()` methods don't return :const:`.errcodes.ErrorCode.TEST_ERROR`.
                    # If the return code is not :const:`.errcodes.ErrorCode.SUCCESS` at this point, it means this is a serious error.
                    # Stop processing right away.
                    return _res

                # Retrieve the last scenario execution.
                assert SCENARIO_STACK.size == 0
                if not SCENARIO_STACK.history:
                    self.error("No last scenario after execution")
                    return ErrorCode.INTERNAL_ERROR
                _scenario_execution = SCENARIO_STACK.history[-1]  # type: ScenarioExecution

                # Manage test errors.
                if _scenario_execution.errors:
                    _errors.append(ErrorCode.TEST_ERROR)

                # Feed the :attr:`.scenarioresults.SCENARIO_RESULTS` instance.
                SCENARIO_RESULTS.add(_scenario_execution)

                # Generate JSON report if required.
                _json_report = ScenarioArgs.getinstance().json_report  # type: typing.Optional[Path]
                if _json_report:
                    SCENARIO_REPORT.writejsonreport(_scenario_execution.definition, _json_report)

            if SCENARIO_RESULTS.count > 1:
                SCENARIO_RESULTS.display()

            # Terminate log features.
            LOGGING_SERVICE.stop()

            # End test.
            return ErrorCode.worst(_errors)

        except TestError as _error:
            # Don't create an `ExceptionError` from a `TestError`.
            # Display it as is.
            _error.logerror(MAIN_LOGGER, logging.ERROR)
            return ErrorCode.INTERNAL_ERROR
        except Exception as _exception:
            # Other kind of exception: use a `ExceptionError` to display it.
            ExceptionError(_exception).logerror(MAIN_LOGGER, logging.ERROR)
            return ErrorCode.INTERNAL_ERROR

    # Scenario execution.

    @property
    def _execution_mode(self):  # type: (...) -> ScenarioRunner.ExecutionMode
        """
        Current execution mode.

        Depends on
        1) the scenario stack building context,
        and 2) the scenario args --doc-only option.
        """
        from .scenarioargs import ScenarioArgs
        from .scenariostack import SCENARIO_STACK

        if SCENARIO_STACK.building.scenario_definition:
            return ScenarioRunner.ExecutionMode.BUILD_OBJECTS
        elif ScenarioArgs.getinstance().doc_only:
            return ScenarioRunner.ExecutionMode.DOC_ONLY
        else:
            return ScenarioRunner.ExecutionMode.EXECUTE

    def executepath(
            self,
            scenario_path,  # type: AnyPathType
    ):  # type: (...) -> ErrorCode
        """
        Executes a scenario from its script path.

        :param scenario_path: Scenario Python script path.
        :return: Error code from the :class:`.errcodes.ErrorCode` enumerate,
                 but no :const:`.errcodes.ErrorCode.TEST_ERROR`.

        Feeds the :attr:`.scenarioresults.SCENARIO_RESULTS` instance.
        """
        from .loggermain import MAIN_LOGGER
        from .scenariodefinition import ScenarioDefinitionHelper
        from .testerrors import ExceptionError

        # Create a test instance.
        try:
            _scenario_definition_class = (
                ScenarioDefinitionHelper.getscenariodefinitionclassfromscript(scenario_path)
            )  # type: typing.Type[ScenarioDefinition]
        except ImportError as _err:
            ExceptionError(_err).logerror(MAIN_LOGGER, logging.ERROR)
            return ErrorCode.INPUT_MISSING_ERROR
        except SyntaxError as _err:
            ExceptionError(_err).logerror(MAIN_LOGGER, logging.ERROR)
            return ErrorCode.INPUT_FORMAT_ERROR
        except LookupError as _err:
            ExceptionError(_err).logerror(MAIN_LOGGER, logging.ERROR)
            return ErrorCode.INPUT_FORMAT_ERROR

        try:
            _scenario_definition = _scenario_definition_class()  # type: ScenarioDefinition
        except Exception as _err:
            # Unexpected exception.
            MAIN_LOGGER.error("Unexpected exception: %s" % str(_err), exc_info=sys.exc_info())
            return ErrorCode.INTERNAL_ERROR

        return self.executescenario(_scenario_definition)

    def executescenario(
            self,
            scenario_definition,  # type: ScenarioDefinition
    ):  # type: (...) -> ErrorCode
        """
        Executes a scenario or subscenario.

        :param scenario_definition: Scenario to execute.
        :return: Error code from the :class:`.errcodes.ErrorCode` enumerate,
                 but no :const:`.errcodes.ErrorCode.TEST_ERROR`.
        """
        self.debug("Executing scenario %s" % repr(scenario_definition))

        # Build and begin the scenario.
        _res = self._buildscenario(scenario_definition)  # type: ErrorCode
        if _res != ErrorCode.SUCCESS:
            return _res
        assert scenario_definition.execution
        _res = self._beginscenario(scenario_definition)
        if _res != ErrorCode.SUCCESS:
            return _res

        # Execute each step in the stack.
        scenario_definition.execution.startsteplist()
        while (not self._shouldstop()) and scenario_definition.execution.current_step_definition:
            # Execute the step.
            self.pushindentation()
            self._execstep(scenario_definition.execution.current_step_definition)
            self.popindentation()

            # Move to next step.
            if scenario_definition.execution.current_step_definition:
                scenario_definition.execution.nextstep()

        # End the scenario.
        _res = self._endscenario(scenario_definition)
        if _res != ErrorCode.SUCCESS:
            return _res

        # Whether a test error occurred or not, return SUCCESS in this method.
        return ErrorCode.SUCCESS

    def _buildscenario(
            self,
            scenario_definition,  # type: ScenarioDefinition
    ):  # type: (...) -> ErrorCode
        """
        Builds a scenario definition.

        :param scenario_definition: :class:`.scenariodefinition.ScenarioDefinition` instance to populate with steps, actions and expected results definitions.
        :return: Error code from the :class:`.errcodes.ErrorCode` enumerate.
        """
        from .scenariodefinition import ScenarioDefinitionHelper
        from .scenarioexecution import ScenarioExecution
        from .scenariostack import SCENARIO_STACK
        from .testerrors import KnownIssue

        self.debug("_buildscenario(scenario_definition='%s')" % repr(scenario_definition))
        self.pushindentation()

        # Inspect the scenario definition class to build step definitions from methods
        ScenarioDefinitionHelper(scenario_definition).buildsteps()

        # Feed the building context of the scenario stack with the scenario definition being built.
        SCENARIO_STACK.building.pushscenariodefinition(scenario_definition)

        # Create the `ScenarioExecution` instance right now.
        # Even though we are only building objects for now,
        # this is required to make it possible to iterate over the step list (just after), and execute them in the `BUILD_OBJECTS` exection mode.
        scenario_definition.execution = ScenarioExecution(scenario_definition)

        # Start iterating over the step list.
        scenario_definition.execution.startsteplist()
        while scenario_definition.execution.current_step_definition:
            self.pushindentation()

            # Mark the step definition known issues already known before executing the step and collecting other known issues.
            # These known issues shall be notified before the actual step execution later on,
            # otherwise they would be notified at the end of the step execution only.
            for _known_issue in scenario_definition.execution.current_step_definition.known_issues:  # type: KnownIssue
                _known_issue.init_only = True

            # Execute the step method in the `BUILD_OBJECTS` exection mode.
            self._execstep(scenario_definition.execution.current_step_definition)

            # Continue iterating over the step list.
            self.popindentation()
            scenario_definition.execution.nextstep()

        # Eventually remove the scenario definition reference from the building context of the scenario stack.
        SCENARIO_STACK.building.popscenariodefinition(scenario_definition)

        self.popindentation()
        return ErrorCode.SUCCESS

    def _beginscenario(
            self,
            scenario_definition,  # type: ScenarioDefinition
    ):  # type: (...) -> ErrorCode
        """
        Begins a scenario or sub-scenario execution.

        :param scenario_definition: Scenario or subscenario which execution to start.
        :return: Error code from the :class:`.errcodes.ErrorCode` enumerate.
        """
        from .handlers import HANDLERS
        from .loggermain import MAIN_LOGGER
        from .scenarioconfig import SCENARIO_CONFIG
        from .scenarioevents import ScenarioEvent, ScenarioEventData
        from .scenariologging import SCENARIO_LOGGING
        from .scenariostack import SCENARIO_STACK

        self.debug("_beginscenario(scenario_definition=%s)" % repr(scenario_definition))
        self.pushindentation()

        # Scenario execution stack management:
        # - Note: The scenario execution instance has already been created in `_buildscenario()`.
        assert scenario_definition.execution
        # - Before pushing the scenario execution to the stack, store the sub-scenario reference in the current action / expected result when applicable.
        if SCENARIO_STACK.current_action_result_execution:
            SCENARIO_STACK.current_action_result_execution.subscenarios.append(scenario_definition.execution)
        # - Eventually push the scenario execution to the execution stack.
        SCENARIO_STACK.pushscenarioexecution(scenario_definition.execution)

        # Test intro.
        SCENARIO_LOGGING.beginscenario(scenario_definition)

        # Check and display that the main scenario attributes.
        # (main scenario only)
        if SCENARIO_STACK.ismainscenario(scenario_definition):
            SCENARIO_LOGGING.beginattributes()

            # Display the declared scenario attributes.
            _scenario_definition_attribute_names = scenario_definition.getattributenames()  # type: typing.List[str]
            for _scenario_definition_attribute_name in _scenario_definition_attribute_names:  # type: str
                SCENARIO_LOGGING.attribute(_scenario_definition_attribute_name, scenario_definition.getattribute(_scenario_definition_attribute_name))

            # Check expected attributes.
            _expected_attribute_names = SCENARIO_CONFIG.expectedscenarioattributes()  # type: typing.List[str]
            self.debug("Expected attributes: %s" % repr(_expected_attribute_names))
            for _expected_attribute_name in _expected_attribute_names:  # type: str
                if _expected_attribute_name not in _scenario_definition_attribute_names:
                    MAIN_LOGGER.error("Missing test attribute %s" % _expected_attribute_name)
                    self.popindentation()
                    return ErrorCode.INPUT_FORMAT_ERROR

            SCENARIO_LOGGING.endattributes()

        # Execute *before test* handlers.
        HANDLERS.callhandlers(ScenarioEvent.BEFORE_TEST, ScenarioEventData.Scenario(scenario_definition=scenario_definition))

        # Start execution time.
        assert scenario_definition.execution
        scenario_definition.execution.time.setstarttime()

        # Notify every known issues registered at the definition level.
        self._notifyknownissuedefinitions(scenario_definition)

        self.popindentation()
        return ErrorCode.SUCCESS

    def _endscenario(
            self,
            scenario_definition,  # type: ScenarioDefinition
    ):  # type: (...) -> ErrorCode
        """
        Ends a scenario or subscenario execution.

        :param scenario_definition: Scenario or subscenario which execution to end.
        :return: Error code from the :class:`.errcodes.ErrorCode` enumerate.
        """
        from .handlers import HANDLERS
        from .scenarioevents import ScenarioEvent, ScenarioEventData
        from .scenariologging import SCENARIO_LOGGING
        from .scenariostack import SCENARIO_STACK

        self.debug("_endscenario(scenario_definition='%s')" % scenario_definition.name)
        self.pushindentation()

        assert SCENARIO_STACK.iscurrentscenario(scenario_definition)
        assert scenario_definition.execution

        # Known issues:
        # - Finish iterating over the steps in order to notify each known issue defined at the definition level.
        while scenario_definition.execution.current_step_definition:
            self._notifyknownissuedefinitions(scenario_definition.execution.current_step_definition)
            scenario_definition.execution.nextstep()
        # - Check that all known issues registered at the definition level have been notified.
        self._notifyknownissuedefinitions(scenario_definition)

        # End execution time.
        scenario_definition.execution.time.setendtime()

        # Execute *after test* handlers (whether the test is SUCCESS or not).
        HANDLERS.callhandlers(ScenarioEvent.AFTER_TEST, ScenarioEventData.Scenario(scenario_definition=scenario_definition))

        # Test outro.
        SCENARIO_LOGGING.endscenario(scenario_definition)

        # Pop the scenario from the stack.
        SCENARIO_STACK.popscenarioexecution()

        if SCENARIO_STACK.size > 0:
            # When errors occurred, and this in not the main scenario,
            # raise the last error in order to break the execution of the parent scenario.
            if scenario_definition.execution.errors:
                raise scenario_definition.execution.errors[-1]

        if SCENARIO_STACK.size == 0:
            SCENARIO_LOGGING.displaystatistics(scenario_definition.execution)

        self.popindentation()
        return ErrorCode.SUCCESS

    def _execstep(
            self,
            step_definition,  # type: StepDefinition
    ):  # type: (...) -> None
        """
        Executes the step.

        :param step_definition: Step definition to execute.
        """
        from .handlers import HANDLERS
        from .scenarioconfig import SCENARIO_CONFIG
        from .scenarioevents import ScenarioEvent, ScenarioEventData
        from .scenariologging import SCENARIO_LOGGING
        from .scenariostack import SCENARIO_STACK
        from .stepexecution import StepExecution
        from .stepsection import StepSection
        from .testerrors import ExceptionError

        self.debug("Beginning of %s" % repr(step_definition))

        if isinstance(step_definition, StepSection):
            if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                SCENARIO_LOGGING.stepsection(step_definition)
        else:
            # Step execution number, starting from 1.
            # Sum up step executions already known for the given scenario.
            _step_number = 1  # type: int
            for _step_definition in step_definition.scenario.steps:  # type: StepDefinition
                # Skip step sections.
                if isinstance(_step_definition, StepSection):
                    continue
                _step_number += len(_step_definition.executions)

            # Execute *before step* handlers.
            if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                HANDLERS.callhandlers(ScenarioEvent.BEFORE_STEP, ScenarioEventData.Step(step_definition=step_definition))
                if self._shouldstop() or (not SCENARIO_STACK.current_step_definition):
                    self.debug("Execution of %s aborted after *before step* handlers" % repr(step_definition))
                    return

            # Start time.
            if self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE:
                step_definition.executions.append(StepExecution(step_definition, _step_number))

            # Display the step description.
            if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                SCENARIO_LOGGING.stepdescription(step_definition)

            # Notify every known issues registered out of the step execution method.
            self._notifyknownissuedefinitions(step_definition, init_only=True)

            # Method execution.
            try:
                self.debug("Executing %s in %s mode" % (repr(step_definition), self._execution_mode.name))
                self.pushindentation()
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
            finally:
                # Ensure the current action/result (if any) is terminated after the step execution.
                if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                    self._endcurrentactionresult()
                self.popindentation()

            # Check that all known issues registered at the definition level have been notified.
            self._notifyknownissuedefinitions(step_definition)

            # End time.
            if self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE:
                step_definition.executions[-1].time.setendtime()

            # Execute *after step* handlers.
            if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
                HANDLERS.callhandlers(ScenarioEvent.AFTER_STEP, ScenarioEventData.Step(step_definition=step_definition))

        self.debug("End of %s" % repr(step_definition))

        # Delay between steps.
        if self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE:
            _delay = SCENARIO_CONFIG.delaybetweensteps()  # type: float
            if self.doexecute() and (_delay > 0.0):
                time.sleep(_delay)

    def onstepdescription(
            self,
            description,  # type: str
    ):  # type: (...) -> None
        """
        Call redirection from :meth:`.scenariodefinition.ScenarioDefinition.STEP()`.

        :param description: Step description.
        """
        from .scenariostack import SCENARIO_STACK

        self.debug("onstepdescription(description='%s')" % description)

        if self._execution_mode == ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            # Build objects.
            if SCENARIO_STACK.building.step_definition:
                SCENARIO_STACK.building.step_definition.description = description
            else:
                SCENARIO_STACK.raisecontexterror("No building step definition")

    def _notifyknownissuedefinitions(
            self,
            step_user_api,  # type: StepUserApi
            init_only=False,  # type: bool
    ):  # type: (...) -> None
        """
        Notifies the known issues declared at the definition level for the given scenario or step definition.

        :param step_user_api: Scenario or step definition to process known issues for.
        :param init_only: ``True`` to process only *init-only* known issues.
        """
        from .testerrors import KnownIssue

        if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            for _known_issue in step_user_api.known_issues:  # type: KnownIssue
                if init_only and not _known_issue.init_only:
                    continue

                self.debug("Notifying known issue from %s" % repr(step_user_api))
                _known_issue.logerror(logger=self, level=logging.DEBUG)
                self.onerror(_known_issue)

    def onactionresult(
            self,
            action_result_type,  # type: ActionResultDefinition.Type
            description,  # type: str
            location,  # type: CodeLocation
    ):  # type: (...) -> None
        """
        Call redirection from :meth:`.scenariodefinition.ScenarioDefinition.ACTION()` or :meth:`.scenariodefinition.ScenarioDefinition.RESULT()`.

        :param action_result_type: ACTION or RESULT.
        :param description: Action or expected result description.
        :param location: Location where the action or expected result is defined.
        """
        from .actionresultexecution import ActionResultExecution
        from .scenariologging import SCENARIO_LOGGING
        from .scenariostack import SCENARIO_STACK

        self.debug("onactionresult(action_result_=%s, description='%s', location='%s')"
                   % (action_result_type, description, location.tolongstring()))

        if self._execution_mode == ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            # Build objects.
            if SCENARIO_STACK.building.step_definition:
                SCENARIO_STACK.building.step_definition.addactionresult(
                    ActionResultDefinition(
                        type=action_result_type,
                        description=description,
                        location=location,
                    )
                )
            else:
                SCENARIO_STACK.raisecontexterror("No building step definition")
        else:
            if SCENARIO_STACK.current_step_definition:
                # Terminate the previous action/result, if any.
                self._endcurrentactionresult()

                # Switch to this action/result.
                _action_result_definition = SCENARIO_STACK.current_step_definition.getactionresult(location=location)  \
                    # type: typing.Optional[ActionResultDefinition]
                assert _action_result_definition and (_action_result_definition.type == action_result_type), (
                    "%s not processed while building the test. Check the conditions around the %s."
                    % (action_result_type, action_result_type)
                )
                if self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE:
                    _action_result_definition.executions.append(ActionResultExecution(_action_result_definition))

                # Memo: When executing in `DOC_ONLY` mode, no current step execution is set.
                if SCENARIO_STACK.current_step_execution:
                    SCENARIO_STACK.current_step_execution.current_action_result_definition = _action_result_definition

                # Display.
                SCENARIO_LOGGING.actionresult(_action_result_definition, description)
            else:
                SCENARIO_STACK.raisecontexterror("No current step definition")

    def _endcurrentactionresult(self):  # type: (...) -> None
        """
        Ends the current action or expected result section.
        """
        from .scenariostack import SCENARIO_STACK

        if self._execution_mode != ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            if SCENARIO_STACK.current_step_execution and SCENARIO_STACK.current_action_result_definition and SCENARIO_STACK.current_action_result_execution:
                self.debug("_endcurrentactionresult(): type=%s, description='%s'"
                           % (SCENARIO_STACK.current_action_result_definition.type, SCENARIO_STACK.current_action_result_definition.description))

                if self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE:
                    SCENARIO_STACK.current_action_result_execution.time.setendtime()

                SCENARIO_STACK.current_step_execution.current_action_result_definition = None

    def onevidence(
            self,
            evidence,  # type: str
    ):  # type: (...) -> None
        """
        Call redirection from :meth:`.scenariodefinition.ScenarioDefinition.EVIDENCE()`.

        :param evidence: Evidence text.
        """
        from .scenariologging import SCENARIO_LOGGING
        from .scenariostack import SCENARIO_STACK

        self.debug("onevidence(evidence=%s)" % repr(evidence))

        if SCENARIO_STACK.current_action_result_execution:
            # Save the execution data.
            SCENARIO_STACK.current_action_result_execution.evidence.append(evidence)
            # Console display.
            SCENARIO_LOGGING.evidence(evidence)
        else:
            SCENARIO_STACK.raisecontexterror("No current action / expected result execution")

    def doexecute(self):  # type: (...) -> bool
        """
        Tells whether the test script shall be executed.

        :return: :const:`True` when the test script shall be executed.
        """
        return self._execution_mode == ScenarioRunner.ExecutionMode.EXECUTE

    def onerror(
            self,
            error,  # type: TestError
            originator=None,  # type: StepUserApi
    ):  # type: (...) -> None
        """
        Called when an error occurs.

        :param error: Error that occurred.
        :param originator: Scenario or step definition that made the call to :meth:`onerror()`, set in :meth:.stepuserapi.StepUserApi.knownissue()`..
        """
        from .actionresultexecution import ActionResultExecution
        from .handlers import HANDLERS
        from .scenarioevents import ScenarioEvent, ScenarioEventData
        from .scenarioexecution import ScenarioExecution
        from .scenariologging import SCENARIO_LOGGING
        from .scenariostack import SCENARIO_STACK
        from .stepexecution import StepExecution
        from .testerrors import KnownIssue

        self.debug("onerror(error=%s, originator=%s)" % (repr(error), repr(originator)))

        if self._execution_mode == ScenarioRunner.ExecutionMode.BUILD_OBJECTS:
            # Build objects.
            if isinstance(error, KnownIssue):
                if originator:
                    SCENARIO_STACK.building.fromoriginator(originator).known_issues.append(error)
                else:
                    SCENARIO_STACK.raisecontexterror("Originator missing for known issue while building objects")
            else:
                # Cannot register the error while building objects.
                # Just raise the error.
                raise error
        else:
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
                _list = obj.warnings if error.iswarning() else obj.errors  # type: typing.List[TestError]
                # Do not store the warnings twice.
                if error.iswarning():
                    for _error in _list:
                        if (_error.location == error.location) and (str(_error) == str(error)):
                            return False
                # Store the error in the candidate list.
                _list.append(error)
                return True
            _store_error(SCENARIO_STACK.current_scenario_execution)
            _store_error(SCENARIO_STACK.current_step_execution)
            _store_current_action_result = True  # type: bool
            if isinstance(error, KnownIssue) and SCENARIO_STACK.current_step_definition and SCENARIO_STACK.current_action_result_execution:
                for _known_issue in SCENARIO_STACK.current_step_definition.known_issues:  # type: KnownIssue
                    if error == _known_issue:
                        # When the known issue had already been declared at the definition level,
                        # do not push it to the action/expected result instance.
                        _store_current_action_result = False
                        break
            if _store_current_action_result:
                _store_error(SCENARIO_STACK.current_action_result_execution)

            # Notify the error.
            if not error.iswarning():
                HANDLERS.callhandlers(ScenarioEvent.ERROR, ScenarioEventData.Error(error=error))

    def _shouldstop(self):  # type: (...) -> bool
        """
        Tells whether the scenario execution should stop.

        :return: ``True`` when the scenario execution should stop, ``False`` when the scenario execution should continue on.
        """
        from .scenarioconfig import SCENARIO_CONFIG
        from .scenariostack import SCENARIO_STACK

        if SCENARIO_STACK.current_scenario_execution and SCENARIO_STACK.current_scenario_execution.errors:
            if not SCENARIO_CONFIG.continueonerror():
                return True
        return False

    def goto(
            self,
            to_step_specification,  # type: StepSpecificationType
    ):  # type: (...) -> None
        """
        Call redirection from :meth:`.scenariodefinition.ScenarioDefinition.goto()`.

        :param to_step_specification: Specification of the next step to execute.
        """
        from .scenariostack import SCENARIO_STACK

        self.debug("Jumping to step '%s'." % repr(to_step_specification))

        if SCENARIO_STACK.current_scenario_definition and SCENARIO_STACK.current_scenario_execution:
            _next_step_definition = SCENARIO_STACK.current_scenario_definition.expectstep(to_step_specification)  # type: StepDefinition
            SCENARIO_STACK.current_scenario_execution.setnextstep(_next_step_definition)
            raise GotoException()
        else:
            SCENARIO_STACK.raisecontexterror("No current scenario definition or execution")


class GotoException(Exception):
    """
    Breaks execution in a step method when :meth:`.scenariodefinition.ScenarioDefinition.goto()` is called.
    """


__doc__ += """
.. py:attribute:: SCENARIO_RUNNER

    Main instance of :class:`ScenarioRunner`.
"""
SCENARIO_RUNNER = ScenarioRunner()  # type: ScenarioRunner
