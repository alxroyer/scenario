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

import logging
import typing

import scenario

if True:
    from . import _datascenarios  # `_datascenarios` used for global instanciation.
if typing.TYPE_CHECKING:
    from ._configvalues import ConfigValuesType as _ConfigValuesType
    from ._expectations import CampaignExpectations as _CampaignExpectationsType
    from ._expectations import ScenarioExpectations as _ScenarioExpectationsType
    from ._expectations import TestSuiteExpectations as _TestTestSuiteExpectationsType


# Export data scenario classes as a `scenarios` attribute.
scenarios = _datascenarios


class _ExpectationRequirements:
    def __init__(
            self,
            attributes,  # type: bool
            steps,  # type: bool
            actions_results,  # type: bool
            error_details,  # type: bool
            stats,  # type: bool
    ):  # type: (...) -> None
        if actions_results:
            scenario.Assertions.asserttrue(steps, "actions_results=True depends on steps=True")

        self.attributes_still_required = attributes  # type: bool
        self.steps_still_required = steps  # type: bool
        self.actions_results_still_required = actions_results  # type: bool
        self.error_details_still_required = error_details  # type: bool
        self.stats_still_required = stats  # type: bool

    def attributes(self):  # type: (...) -> bool
        if self.attributes_still_required:
            self.attributes_still_required = False
            return True
        return False

    def steps(self):  # type: (...) -> bool
        if self.steps_still_required:
            self.steps_still_required = False
            return True
        return False

    def actionsresults(self):  # type: (...) -> bool
        if self.actions_results_still_required:
            self.actions_results_still_required = False
            return True
        return False

    def errordetails(self):  # type: (...) -> bool
        if self.error_details_still_required:
            self.error_details_still_required = False
            return True
        return False

    def stats(self):  # type: (...) -> bool
        if self.stats_still_required:
            self.stats_still_required = False
            return True
        return False


def scenarioexpectations(
        script_path,  # type: scenario.Path
        doc_only=False,  # type: bool
        continue_on_error=False,  # type: bool
        attributes=False,  # type: bool
        steps=False,  # type: bool
        actions_results=False,  # type: bool
        error_details=False,  # type: bool
        stats=False,  # type: bool
        config_values=None,  # type: _ConfigValuesType
):  # type: (...) -> _ScenarioExpectationsType
    """
    Builds a :class:`._expectations.ScenarioExpectations` instance for the given scenario.

    :param script_path: Scenario to build a :class:`._expectations.ScenarioExpectations` instance for.
    :param doc_only: ``True`` when the scenario is executed in *doc-only* mode.
    :param continue_on_error: ``True`` to generate expectations in *continue_on_error* mode.
    :param attributes: ``True`` to build attribute expectations.
    :param steps: ``True`` to build step expectations.
    :param actions_results: ``True`` to build action/result expectations.
    :param error_details: ``True`` to set error expectations.
    :param stats: ``True`` to build statistics expectations.
    :param config_values: Extra configurations.
    :return: :class:`._expectations.ScenarioExpectations` instance.
    """
    from . import _configvalues as _configvalues
    from ._expectations import ErrorExpectations, NOT_SET, ScenarioExpectations
    from . import _paths as _paths

    _reqs = _ExpectationRequirements(
        attributes=attributes,
        steps=steps,
        actions_results=actions_results,
        error_details=error_details,
        stats=stats,
    )  # type: _ExpectationRequirements

    _scenario_expectations = ScenarioExpectations(script_path)  # type: ScenarioExpectations
    # Set SUCCESS, no error and no warning by default. Let the tests below amend this information.
    _scenario_expectations.status = scenario.ExecutionStatus.SUCCESS
    if error_details:
        _scenario_expectations.noerror()
        _scenario_expectations.nowarning()

    if script_path.samefile(_paths.ACTION_RESULT_LOOP_SCENARIO):
        def _actionresultloopscenario():  # type: (...) -> None
            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Action/result loop sample scenario")
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=1, actions=10, results=10)
                else:
                    _scenario_expectations.setstats(steps=(1, 1), actions=(10, 10), results=(10, 10))
            if _reqs.steps():
                _scenario_expectations.addstep(number=1, name="step010")
                if _reqs.actionsresults():
                    for _i in range(10):  # type: int
                        _scenario_expectations.step("step010").addaction(f"Action #{_i + 1}")
                        _scenario_expectations.step("step010").addresult(f"Expected result #{_i + 1}")
        _actionresultloopscenario()

    elif script_path.samefile(_paths.CONFIG_DB_SCENARIO):
        def _configdbscenario():  # type: (...) -> None
            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Configuration database sample scenario")
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=3, actions=3, results=0)
                else:
                    _scenario_expectations.setstats(steps=(3, 3), actions=(3, 3), results=(0, 0))
        _configdbscenario()

    elif script_path.samefile(_paths.FAILING_SCENARIO):
        def _failingscenario():  # type: (...) -> None
            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Failing scenario sample")
            if _reqs.steps():
                _scenario_expectations.addstep(number=1, name="step010")
                if doc_only or continue_on_error:
                    _scenario_expectations.addstep(number=2, name="step020")
                if _reqs.actionsresults():
                    # step010
                    _scenario_expectations.step("step010").addaction("Memorize 'step010-1' as the last checkpoint.")
                    _scenario_expectations.step("step010").addaction("Generate an exception without catching it.")
                    if doc_only:
                        _scenario_expectations.step("step010").addresult("The exception is thrown.")
                        _scenario_expectations.step("step010").addaction("Memorize 'step010-2' as the last checkpoint.")
                    # step020
                    if doc_only or continue_on_error:
                        _scenario_expectations.step("step020").addaction("Check the last checkpoint.")
                        _scenario_expectations.step("step020").addresult("The last checkpoint is... whatever.")
                        _scenario_expectations.step("step020").addaction("Memorize 'step020-1' as the last checkpoint.")
            if not doc_only:
                _scenario_expectations.status = scenario.ExecutionStatus.FAIL
            if _reqs.errordetails():
                if not doc_only:
                    _scenario_expectations.adderror(ErrorExpectations(
                        cls=scenario.ExceptionError, exception_type="AssertionError", message="This is an exception.",
                        location=f"{_paths.FAILING_SCENARIO}:39:FailingScenario.step010",  # location: FAILING_SCENARIO/step010-exception
                    ))
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=2, actions=5, results=2)
                elif continue_on_error:
                    _scenario_expectations.setstats(steps=(2, 2), actions=(4, 5), results=(1, 2))
                else:
                    _scenario_expectations.setstats(steps=(1, 2), actions=(2, 5), results=(0, 2))
        _failingscenario()

    elif script_path.samefile(_paths.GOTO_SCENARIO):
        def _gotoscenario():  # type: (...) -> None
            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Goto scenario sample")
            if _reqs.steps():
                if doc_only:
                    _scenario_expectations.addstep(number=1, name="step000")
                    _scenario_expectations.addstep(number=2, name="step010")
                    _scenario_expectations.addstep(number=3, name="step020")
                    _scenario_expectations.addstep(number=4, name="step030")
                    _scenario_expectations.addstep(number=5, name="step040")
                else:
                    _scenario_expectations.addstep(number=1, name="step000")
                    _scenario_expectations.addstep(number=2, name="step010")
                    _scenario_expectations.addstep(number=3, name="step020")
                    _scenario_expectations.addstep(number=4, name="step010")
                    _scenario_expectations.addstep(number=5, name="step020")
                    _scenario_expectations.addstep(number=6, name="step040")
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=5, actions=6, results=2)
                else:
                    _scenario_expectations.setstats(steps=(6, 5), actions=(6, 6), results=(2, 2))
        _gotoscenario()

    elif script_path.samefile(_paths.INHERITING_SCENARIO):
        def _inheritingscenario():  # type: (...) -> None
            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Inheriting scenario sample")
            if _reqs.steps():
                _scenario_expectations.addstep(number=1, name="step010")
                _scenario_expectations.addstep(number=2, name="step015")
                _scenario_expectations.addstep(number=3, name="step020")
                _scenario_expectations.addstep(number=4, name="step030")
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=4, actions=4, results=4)
                else:
                    _scenario_expectations.setstats(steps=(4, 4), actions=(4, 4), results=(4, 4))
        _inheritingscenario()

    elif script_path.samefile(_paths.KNOWN_ISSUE_DETAILS_SCENARIO):
        def _knownissuedetailsscenario():  # type: (...) -> None
            from knownissuedetailsscenario import KnownIssueDetailsScenario

            _ConfigKey = KnownIssueDetailsScenario.ConfigKey  # type: typing.Type[KnownIssueDetailsScenario.ConfigKey]
            _known_issue_level = _configvalues.getint(config_values, _ConfigKey.LEVEL, default=0) or None  # type: typing.Optional[int]
            _known_issue_id = _configvalues.getstr(config_values, _ConfigKey.ID, default="") or None  # type: typing.Optional[str]
            _known_issue_url_base = _configvalues.getstr(config_values, _ConfigKey.URL_BASE, default="") or None  # type: typing.Optional[str]
            _issue_level_ignored = _configvalues.getint(config_values, scenario.ConfigKey.ISSUE_LEVEL_IGNORED, default=0) or None  # type: typing.Optional[int]
            _issue_level_error = _configvalues.getint(config_values, scenario.ConfigKey.ISSUE_LEVEL_ERROR, default=0) or None  # type: typing.Optional[int]

            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Known issue details scenario sample")
            if _reqs.steps():
                _scenario_expectations.addstep(number=1, name="step010")
            # Memo: Known issue is generated inside an action bloc.
            if doc_only:
                _scenario_expectations.status = scenario.ExecutionStatus.SUCCESS
            elif (_issue_level_error is not None) and ((_known_issue_level is None) or (_known_issue_level >= _issue_level_error)):
                _scenario_expectations.status = scenario.ExecutionStatus.FAIL
            elif (_issue_level_ignored is not None) and (_known_issue_level is not None) and (_known_issue_level <= _issue_level_ignored):
                _scenario_expectations.status = scenario.ExecutionStatus.SUCCESS
            else:
                _scenario_expectations.status = scenario.ExecutionStatus.WARNINGS
            if _reqs.errordetails():
                if _scenario_expectations.status != scenario.ExecutionStatus.SUCCESS:
                    _scenario_expectations.adderror(
                        level=(
                            logging.ERROR if _scenario_expectations.status == scenario.ExecutionStatus.FAIL
                            else logging.WARNING
                        ),
                        error=ErrorExpectations(
                            cls=scenario.KnownIssue,
                            level=_known_issue_level if _known_issue_level is not None else NOT_SET,
                            id=_known_issue_id if _known_issue_id is not None else NOT_SET,
                            url=(
                                f"{_known_issue_url_base.rstrip('/')}/{_known_issue_id.lstrip('#')}"
                                if (_known_issue_id is not None) and (_known_issue_url_base is not None)
                                else NOT_SET
                            ),
                            message=f"Known issue with level {_known_issue_level} and id {_known_issue_id!r}",
                            # Don't check the location.
                            location=None,
                        ),
                    )
            if _reqs.stats():
                _scenario_expectations.setstats(steps=1, actions=4 if _known_issue_url_base else 3, results=0)
        _knownissuedetailsscenario()

    elif script_path.samefile(_paths.KNOWN_ISSUES_SCENARIO):
        def _knownissuesscenario():  # type: (...) -> None
            from knownissuesscenario import KnownIssuesScenario

            _known_issue_level = (
                logging.ERROR if _configvalues.getint(config_values, scenario.ConfigKey.ISSUE_LEVEL_ERROR, default=0)
                else logging.WARNING
            )  # type: int
            _raise_exceptions = _configvalues.getbool(config_values, KnownIssuesScenario.ConfigKey.RAISE_EXCEPTIONS, default=False)  # type: bool

            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Known issue scenario sample")
            if _reqs.steps():
                _scenario_expectations.addstep(number=1, name="KnownIssuesScenario.KnownIssuesStep")
                if (not _raise_exceptions) or doc_only or continue_on_error:
                    _scenario_expectations.addstep(number=2, name="step010")
                    _scenario_expectations.addstep(number=3, name="step020")
            if _known_issue_level == logging.ERROR:
                _scenario_expectations.status = scenario.ExecutionStatus.FAIL
            else:
                _scenario_expectations.status = scenario.ExecutionStatus.WARNINGS
            if _raise_exceptions and (not doc_only):
                _scenario_expectations.status = scenario.ExecutionStatus.FAIL
            if _reqs.errordetails():
                # Scenario initializer:
                # - Known issue #---
                _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                    cls=scenario.KnownIssue, level=NOT_SET, id="#---", message="Known issue in KnownIssuesScenario.__init__()",
                    location=f"{_paths.KNOWN_ISSUES_SCENARIO}:32:KnownIssuesScenario.__init__",  # location: KNOWN_ISSUES_SCENARIO/#---
                ))
                # KnownIssueStep:
                # - Known issue #000
                _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                    cls=scenario.KnownIssue, level=NOT_SET, id="#000", message="Known issue in KnownIssuesStep.__init__()",
                    location=f"{_paths.KNOWN_ISSUES_SCENARIO}:40:KnownIssuesScenario.KnownIssuesStep.__init__",  # location: KNOWN_ISSUES_SCENARIO/#000
                ))
                # - Known issue #001
                _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                    cls=scenario.KnownIssue, level=NOT_SET, id="#001", message="Known issue in KnownIssuesStep.step() before ACTION/RESULT",
                    location=f"{_paths.KNOWN_ISSUES_SCENARIO}:45:KnownIssuesScenario.KnownIssuesStep.step",  # location: KNOWN_ISSUES_SCENARIO/#001
                ))
                # - Known issue #002
                if not doc_only:
                    _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                        cls=scenario.KnownIssue, level=NOT_SET, id="#002", message="Known issue in KnownIssuesStep.step() under ACTION",
                        location=f"{_paths.KNOWN_ISSUES_SCENARIO}:48:KnownIssuesScenario.KnownIssuesStep.step",  # location: KNOWN_ISSUES_SCENARIO/#002
                    ))
                # - Exception!
                if _raise_exceptions:
                    if not doc_only:
                        _scenario_expectations.adderror(level=logging.ERROR, error=ErrorExpectations(
                            cls=scenario.ExceptionError, exception_type="AssertionError", message="This is an exception.",
                            location=f"{_paths.KNOWN_ISSUES_SCENARIO}:52:KnownIssuesScenario.KnownIssuesStep.step",  # location: KNOWN_ISSUES_SCENARIO/Step-fail
                        ))
                # - Known issue #003
                if not doc_only:
                    if not _raise_exceptions:
                        _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                            cls=scenario.KnownIssue, level=NOT_SET, id="#003", message="Known issue in KnownIssuesStep.step() under ACTION",
                            location=f"{_paths.KNOWN_ISSUES_SCENARIO}:57:KnownIssuesScenario.KnownIssuesStep.step",  # location: KNOWN_ISSUES_SCENARIO/#003
                        ))
                # - Known issue #004
                _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                    cls=scenario.KnownIssue, level=NOT_SET, id="#004", message="Known issue in KnownIssuesStep.step() after ACTION/RESULT",
                    location=f"{_paths.KNOWN_ISSUES_SCENARIO}:59:KnownIssuesScenario.KnownIssuesStep.step",  # location: KNOWN_ISSUES_SCENARIO/#004
                ))
                # step010:
                # - Known issue #011
                _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                    cls=scenario.KnownIssue, level=NOT_SET, id="#011", message="Known issue in KnownIssuesScenario.step010() before ACTION/RESULT",
                    location=f"{_paths.KNOWN_ISSUES_SCENARIO}:64:KnownIssuesScenario.step010",  # location: KNOWN_ISSUES_SCENARIO/#011
                ))
                # - Known issue #012
                if not doc_only:
                    if (not _raise_exceptions) or continue_on_error:
                        _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                            cls=scenario.KnownIssue, level=NOT_SET, id="#012", message="Known issue in KnownIssuesScenario.step010() under ACTION",
                            location=f"{_paths.KNOWN_ISSUES_SCENARIO}:67:KnownIssuesScenario.step010",  # location: KNOWN_ISSUES_SCENARIO/#012
                        ))
                # - Exception!
                if _raise_exceptions and continue_on_error:
                    if not doc_only:
                        _scenario_expectations.adderror(level=logging.ERROR, error=ErrorExpectations(
                            cls=scenario.ExceptionError, exception_type="AssertionError", message="This is an exception.",
                            location=f"{_paths.KNOWN_ISSUES_SCENARIO}:71:KnownIssuesScenario.step010",  # location: KNOWN_ISSUES_SCENARIO/step010-fail
                        ))
                # - Known issue #013
                if not doc_only:
                    if not _raise_exceptions:
                        _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                            cls=scenario.KnownIssue, level=NOT_SET, id="#013", message="Known issue in KnownIssuesScenario.step010() under ACTION",
                            location=f"{_paths.KNOWN_ISSUES_SCENARIO}:76:KnownIssuesScenario.step010",  # location: KNOWN_ISSUES_SCENARIO/#013
                        ))
                # - Known issue #014
                _scenario_expectations.adderror(level=_known_issue_level, error=ErrorExpectations(
                    cls=scenario.KnownIssue, level=NOT_SET, id="#014", message="Known issue in KnownIssuesScenario.step010() after ACTION/RESULT",
                    location=f"{_paths.KNOWN_ISSUES_SCENARIO}:78:KnownIssuesScenario.step010",  # location: KNOWN_ISSUES_SCENARIO/#014
                ))
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=3, actions=7, results=0)
                elif not _raise_exceptions:
                    _scenario_expectations.setstats(steps=(3, 3), actions=(7, 7), results=(0, 0))
                else:
                    _scenario_expectations.setstats(steps=(1, 3), actions=(2, 7), results=(0, 0))
        _knownissuesscenario()

    elif script_path.samefile(_paths.LOGGER_SCENARIO):
        def _loggerscenario():  # type: (...) -> None
            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Logger scenario sample")
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=2, actions=8, results=0)
                else:
                    _scenario_expectations.setstats(steps=(2, 2), actions=(8, 8), results=(0, 0))
        _loggerscenario()

    elif script_path.samefile(_paths.LOGGING_INDENTATION_SCENARIO):
        def _loggingindentationscenario():  # type: (...) -> None
            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Logging indentation scenario sample")
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=1, actions=31, results=0)
                else:
                    _scenario_expectations.setstats(steps=(1, 1), actions=(31, 31), results=(0, 0))
        _loggingindentationscenario()

    elif script_path.samefile(_paths.SCENARIO_LOGGING_SCENARIO):
        def _scenariologgingscenario():  # type: (...) -> None
            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Scenario logging scenario sample")
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=1, actions=1, results=1)
                else:
                    _scenario_expectations.setstats(steps=(1, 1), actions=(1, 1), results=(1, 1))
        _scenariologgingscenario()

    elif script_path.samefile(_paths.SIMPLE_SCENARIO):
        def _simplescenario():  # type: (...) -> None
            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Simple scenario sample")
            if _reqs.steps():
                _scenario_expectations.addstep(number=1, name="step010")
                _scenario_expectations.addstep(number=2, name="step020")
                _scenario_expectations.addstep(number=3, name="step030")
                if _reqs.actionsresults():
                    _scenario_expectations.step("step010").addaction("Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                                                                     "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")
                    _scenario_expectations.step("step010").addresult("Et leo duis ut diam.")
                    _scenario_expectations.step("step020").addaction("Vitae turpis massa sed elementum.")
                    _scenario_expectations.step("step020").addresult("Faucibus a pellentesque sit amet.")
                    _scenario_expectations.step("step030").addaction("Quam id leo in vitae turpis massa sed elementum.")
                    _scenario_expectations.step("step030").addresult("In aliquam sem fringilla ut morbi tincidunt augue interdum velit.")
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=3, actions=3, results=3)
                else:
                    _scenario_expectations.setstats(steps=(3, 3), actions=(3, 3), results=(3, 3))
        _simplescenario()

    elif script_path.samefile(_paths.SUPERSCENARIO_SCENARIO):
        def _superscenarioscenario():  # type: (...) -> None
            from superscenario import SuperScenario

            _ConfigKey = SuperScenario.ConfigKey  # type: typing.Type[SuperScenario.ConfigKey]
            _subscenario_path = _configvalues.getpath(config_values, _ConfigKey.SUBSCENARIO_PATH, default=_paths.SIMPLE_SCENARIO)  # type: scenario.Path

            # Compute the subscenario expectations whatever, so that we can adjust the status, error and statistics expectations appropriately.
            _subscenario_expectations = scenarioexpectations(
                _subscenario_path,
                doc_only=False,
                attributes=attributes,
                steps=steps,
                actions_results=actions_results,
                error_details=error_details,
                stats=stats,
            )  # type: ScenarioExpectations
            assert _subscenario_expectations.status

            if _reqs.attributes():
                _scenario_expectations.addattribute("TITLE", "Subscenario sample")
            if _reqs.steps():
                # One single step.
                _scenario_expectations.addstep(number=1, name="step001", description="Subscenario execution")
                if _reqs.actionsresults():
                    # Action
                    _scenario_expectations.step("step001").addaction(f"Execute the '{_subscenario_path}' scenario.")
                    if doc_only:
                        _scenario_expectations.step("step001").action(0).nosubscenarios()
                    else:
                        _scenario_expectations.step("step001").action(0).addsubscenario(_subscenario_expectations)
                    # Result: only if the subscenario succeeded (or not executed).
                    if doc_only or _subscenario_expectations.status == scenario.ExecutionStatus.SUCCESS:
                        _scenario_expectations.step("step001").addresult("No exception is thrown.")
            # The status of the super-scenario will be the one of the subscenario.
            if not doc_only:
                _scenario_expectations.status = _subscenario_expectations.status
            # The errors should be propagated as is from the subscenario to the super-scenario.
            if _reqs.errordetails():
                if not doc_only:
                    assert _subscenario_expectations.errors is not None
                    for _subscenario_error in _subscenario_expectations.errors:  # type: ErrorExpectations
                        _scenario_expectations.adderror(_subscenario_error)
            if _reqs.stats():
                if doc_only:
                    _scenario_expectations.setstats(steps=1, actions=1, results=1)
                else:
                    _scenario_expectations.setstats(
                        # 1 step in any case.
                        steps=(1, 1),
                        # 1 action in any case.
                        actions=(1, 1),
                        # The result will be executed only when the subscenario does not throw an expcetion.
                        results=(1 if _subscenario_expectations.status == scenario.ExecutionStatus.SUCCESS else 0, 1),
                    )
        _superscenarioscenario()

    if _scenario_expectations.status == scenario.ExecutionStatus.SUCCESS:
        # Error details have already been set to none at the beginning of this function.
        # Ensure the requirement is fulfilled.
        _reqs.errordetails()

    assert not _reqs.attributes_still_required, f"attributes=True not implemented for '{script_path}'"
    assert not _reqs.steps_still_required, f"steps=True not implemented for '{script_path}'"
    assert not _reqs.actions_results_still_required, f"actions_results=True not implemented for '{script_path}'"
    assert not _reqs.error_details_still_required, f"error_details=True not implemented for '{script_path}'"
    assert not _reqs.stats_still_required, f"stats=True not implemented for '{script_path}'"

    return _scenario_expectations


def testsuiteexpectations(
        campaign_expectations,  # type: _CampaignExpectationsType
        test_suite_path,  # type: scenario.Path
        doc_only=False,  # type: bool
        continue_on_error=False,  # type: bool
        attributes=False,  # type: bool
        steps=False,  # type: bool
        actions_results=False,  # type: bool
        error_details=False,  # type: bool
        stats=False,  # type: bool
        config_values=None,  # type: _ConfigValuesType
):  # type: (...) -> _TestTestSuiteExpectationsType
    from . import _paths as _paths

    _test_suite_expectations = campaign_expectations.addtestsuite(test_suite_path)  # type: _TestTestSuiteExpectationsType
    _test_suite_expectations.test_case_expectations = []

    if test_suite_path.samefile(_paths.TEST_DATA_TEST_SUITE):
        for _script_path in _paths.DATA_PATH.glob("*.py"):  # type: scenario.Path
            if _script_path == _paths.WAITING_SCENARIO:
                continue
            _test_suite_expectations.test_case_expectations.append(scenarioexpectations(
                _script_path,
                doc_only=doc_only, continue_on_error=continue_on_error,
                attributes=attributes, steps=steps, actions_results=actions_results, error_details=error_details, stats=stats,
                config_values=config_values,
            ))

    elif test_suite_path.samefile(_paths.DEMO_TEST_SUITE):
        for _script_path in _paths.DEMO_PATH.glob("*.py"):  # type already declared above.
            if _script_path.name in ("htmltestlib.py", "run-demo.py"):
                continue
            _test_suite_expectations.test_case_expectations.append(scenarioexpectations(
                _script_path,
                doc_only=doc_only, continue_on_error=continue_on_error,
                attributes=attributes, steps=steps, actions_results=actions_results, error_details=error_details, stats=stats,
                config_values=config_values,
            ))

    else:
        scenario.Assertions.fail(f"Unknown test suite '{test_suite_path}'")

    return _test_suite_expectations
