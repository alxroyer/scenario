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
Requirement traceability reports.
"""

import abc
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
    from ._reqref import ReqRef as _ReqRefImpl  # `ReqRef` imported once for performance concerns.
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionImpl  # `ScenarioDefinition` imported once for performance concerns.
    from ._scenariodefinition import ScenarioDefinitionHelper as _ScenarioDefinitionHelperImpl  # Same for `ScenarioDefinitionHelper`.
    from ._stepdefinition import StepDefinition as _StepDefinitionImpl  # `StepDefinition` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._campaignexecution import CampaignExecution as _CampaignExecutionType
    from ._jsondictutils import JsonDictType as _JsonDictType
    from ._path import Path as _PathType
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._stepdefinition import StepDefinition as _StepDefinitionType


class ReqTraceability(_LoggerImpl):
    """
    Requirement traceability computation.

    Instantiated once with the :data:`REQ_TRACEABILITY` singleton.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes instance attributes and configures logging for the :class:`ReqTraceability` class.
        """
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, DebugClass.REQ_TRACEABILITY)

        #: Scenarios loaded with :meth:`loaddatafromfiles()` or :meth:`loaddatafromcampaignresults()`.
        self.scenarios = []  # type: typing.List[_ScenarioDefinitionType]

    def loaddatafromfiles(
            self,
            *,
            req_db_file_paths=None,  # type: typing.Iterable[_PathType]
            test_suite_paths=None,  # type: typing.Iterable[_PathType]
            log_info=True,  # type: bool
    ):  # type: (...) -> None
        """
        Loads or reloads input data for requirement traceability computation,
        from requirement and/or test suite files.

        :param req_db_file_paths:
            Optional requirement database file to load.

            If not set, the :attr:`._scenarioconfig.ScenarioConfig.Key.REQ_DB_FILES` configuration will be taken into account.

            If :attr:`._scenarioconfig.ScenarioConfig.Key.REQ_DB_FILES` configuration is not set,
            the requirement database is left as is.
        :param test_suite_paths:
            Optional test suite paths to load scenarios from.

            If not set, the :attr:`._scenarioconfig.ScenarioConfig.Key.TEST_SUITE_FILES` configuration will be taken into account.

            If :attr:`._scenarioconfig.ScenarioConfig.Key.TEST_SUITE_FILES` configuration is not set,
            the scenario list is left as is.
        :param log_info:
            ``True`` (by default) to generate info logging.
        """
        from ._loggermain import MAIN_LOGGER
        from ._reqdb import REQ_DB
        from ._testsuitefile import TestSuiteFile

        self.debug("ReqTraceability.loaddatafromfiles(req_db_file_paths=%r, test_suite_paths=%r)", req_db_file_paths, test_suite_paths)

        # Requirements.

        if req_db_file_paths:
            # Ensure persistent and countable list.
            req_db_file_paths = list(req_db_file_paths)
        else:
            # Default configuration.
            req_db_file_paths = _FAST_PATH.scenario_config.reqdbfiles()

        import time
        _t0 = time.time()  # type: float
        if req_db_file_paths:
            if log_info:
                MAIN_LOGGER.info("Loading requirements")
            with MAIN_LOGGER.pushindentation("  "):
                if REQ_DB.getallreqs():
                    if log_info:
                        MAIN_LOGGER.info("Resetting requirement database")
                    REQ_DB.clear()

                self.debug("Reading %d req-db file(s)", len(list(req_db_file_paths)))
                for _req_db_file_path in req_db_file_paths:  # type: _PathType
                    if log_info:
                        MAIN_LOGGER.info(f"Loading '{_req_db_file_path}'")
                    REQ_DB.load(_req_db_file_path)
        else:
            self.debug("Requirement database left as is")

        if log_info:
            _req_ref_count = len(REQ_DB.getallrefs())  # type: int
            # MAIN_LOGGER.info(f"{_req_ref_count} requirement reference{'' if (_req_ref_count == 1) else 's'} loaded")
            MAIN_LOGGER.info(f"{_req_ref_count} requirement reference{'' if (_req_ref_count == 1) else 's'} loaded in {time.time() - _t0:.3f} seconds")

        # Test suites.

        _t0 = time.time()  # Type already declared above.
        if test_suite_paths:
            # Ensure persistent and countable list.
            test_suite_paths = list(test_suite_paths)
        else:
            # Default configuration.
            test_suite_paths = _FAST_PATH.scenario_config.testsuitefiles()

        if test_suite_paths:
            if log_info:
                MAIN_LOGGER.info("Loading scenarios")
            with MAIN_LOGGER.pushindentation("  "):
                self.scenarios.clear()

                self.debug("Reading %d test suite file(s)", len(list(test_suite_paths)))
                for _test_suite_path in test_suite_paths:  # type: _PathType
                    if log_info:
                        MAIN_LOGGER.info("Loading '%s'", _test_suite_path)
                    with MAIN_LOGGER.pushindentation("  "):
                        _test_suite_file = TestSuiteFile(_test_suite_path)  # type: TestSuiteFile
                        _test_suite_file.read()
                        for _test_script_path in _test_suite_file.script_paths:  # type: _PathType
                            if log_info:
                                MAIN_LOGGER.info("Loading '%s'", _test_script_path)

                            # Find the scenario class.
                            _scenario_definition_class = _ScenarioDefinitionHelperImpl.getscenariodefinitionclassfromscript(
                                _test_script_path,
                                # Avoid loaded module being saved in `sys.modules`,
                                # so that the function can be called again, and traceability refreshed.
                                sys_modules_cache=False,
                            )  # type: typing.Type[_ScenarioDefinitionType]
                            self.debug("_scenario_definition_class=%r", _scenario_definition_class)

                            try:
                                # Disable scenario debug logging.
                                _initial_scenario_debug_logging = (
                                    _FAST_PATH.config_db.get(_FAST_PATH.scenario_config.Key.SCENARIO_DEBUG_LOGGING_ENABLED, type=bool)
                                )  # type: typing.Optional[bool]
                                _FAST_PATH.config_db.set(_FAST_PATH.scenario_config.Key.SCENARIO_DEBUG_LOGGING_ENABLED, False)

                                # Create the scenario instance.
                                _scenario = _scenario_definition_class()  # type: _ScenarioDefinitionType
                            finally:
                                # Restore initial scenario debug logging configuration.
                                _FAST_PATH.config_db.set(_FAST_PATH.scenario_config.Key.SCENARIO_DEBUG_LOGGING_ENABLED, _initial_scenario_debug_logging)
                            self.debug("_scenario=%r", _scenario)
                            self.scenarios.append(_scenario)
        else:
            self.debug("Scenario list left as is")

        if log_info:
            _scenario_count = len(self.scenarios)  # type: int
            # MAIN_LOGGER.info(f"{_scenario_count} scenario{'' if (_scenario_count == 1) else 's'} loaded")
            MAIN_LOGGER.info(f"{_scenario_count} scenario{'' if (_scenario_count == 1) else 's'} loaded in {time.time() - _t0:.3f} seconds")

    def loaddatafromcampaignresults(
            self,
            campaign_results,  # type: typing.Union[_PathType, _CampaignExecutionType]
            log_info=True,  # type: bool
    ):  # type: (...) -> None
        """
        Loads or reloads input data for requirement traceability computation,
        from campaign execution results.

        :param campaign_results:
            Campaign results to load data from.

            The campaign may have been executed with ``--doc-only``.
        :param log_info:
            ``True`` (by default) to generate info logging.
        """
        from ._campaignexecution import CampaignExecution, TestCaseExecution, TestSuiteExecution
        from ._campaignreport import CAMPAIGN_REPORT
        from ._loggermain import MAIN_LOGGER
        from ._reqdb import REQ_DB

        self.debug("ReqTraceability.loaddatafromcampaignresults(campaign_results='%s')", campaign_results)

        if isinstance(campaign_results, _PathImpl):
            # Determine the path of the campaign report file.
            _campaign_report_path = campaign_results  # type: _PathType
            if _campaign_report_path.is_dir():
                _campaign_report_path = CampaignExecution(_campaign_report_path).campaign_report_path
                if not _campaign_report_path.is_file():
                    raise FileNotFoundError(f"No campaign file  found in '{campaign_results}'")
            self.debug("Campaign report file: '%s'", _campaign_report_path)

            # Clear the requirement database before reloading it while reading campaign results.
            if REQ_DB.getallreqs():
                if log_info:
                    MAIN_LOGGER.info("Resetting requirement database")
                REQ_DB.clear()

            if log_info:
                MAIN_LOGGER.info(f"Loading campaign results from '{_campaign_report_path}'")
            _campaign_execution = CAMPAIGN_REPORT.readcampaignreport(
                _campaign_report_path,
                feed_req_db=True,
                # Let's read scenario reports one by one after.
                read_scenario_reports=False,
            )  # type: CampaignExecution

            if log_info:
                _req_ref_count = len(REQ_DB.getallrefs())  # type: int
                MAIN_LOGGER.info(f"{_req_ref_count} requirement reference{'' if (_req_ref_count == 1) else 's'} loaded")
        else:
            _campaign_report_path = campaign_results.campaign_report_path  # Type already declared above.
            _campaign_execution = campaign_results  # Type already declared above.

        self.debug("Saving scenarios from %r", _campaign_execution)
        with self.pushindentation("  "):
            self.scenarios.clear()

            self.debug("Walking through %d test suite execution(s)", len(_campaign_execution.test_suite_executions))
            for _test_suite_execution in _campaign_execution.test_suite_executions:  # type: TestSuiteExecution
                self.debug("Test suite '%s': Walking through %d test case execution(s)",
                           _test_suite_execution.test_suite_file.path, len(_test_suite_execution.test_case_executions))
                with self.pushindentation("  "):
                    for _test_case_execution in _test_suite_execution.test_case_executions:  # type: TestCaseExecution
                        try:
                            if not _test_case_execution.scenario_execution:
                                _test_case_execution.report.read()
                                assert _test_case_execution.scenario_execution
                            self.scenarios.append(_test_case_execution.scenario_execution.definition)
                        except Exception as _err:
                            if _test_case_execution.report.path:
                                MAIN_LOGGER.warning(f"Can't load scenario {_test_case_execution.name!r} from '{_test_case_execution.report.path}': {_err}")
                            else:
                                MAIN_LOGGER.warning(f"Can't load scenario {_test_case_execution.name!r}: {_err}")

        if log_info:
            _scenario_count = len(self.scenarios)  # type: int
            MAIN_LOGGER.info(f"{_scenario_count} scenario{'' if (_scenario_count == 1) else 's'} loaded")

    class Downstream(abc.ABC):
        """
        Classes that describe a downstream traceability.

        Downstream traceability is a matrix starting with requirement references, verified by scenarios and steps.
        """

        #: JSON schema subpath from :attr:`._pkginfo.PackageInfo.repo_url`, for downstream traceability reports.
        JSON_SCHEMA_SUBPATH = "schemas/downstream-traceability.schema.json"  # type: str

        @staticmethod
        def tojson(
                downstream_traceability,  # type: ReqDownstreamTraceabilityType
                *,
                allow_results=True,  # type: bool
        ):  # type: (...) -> _JsonDictType
            """
            JSON content generation for a downstream traceability.

            :param downstream_traceability: Downstream traceability to generate JSON content for.
            :param allow_results: ``False`` to prevent test results in the JSON content.
            :return: Downstream traceability JSON content.
            """
            _json = {}  # type: _JsonDictType
            for _downstream_req_ref in downstream_traceability:  # type: ReqTraceability.Downstream.ReqRef
                _json[_downstream_req_ref.req_ref.id] = _downstream_req_ref.tojson(allow_results=allow_results)
            return _json

        class ReqRef:
            """
            Main entry for downstream traceability.

            Either a main requirement reference, or a subreference.
            """

            def __init__(
                    self,
                    req_ref,  # type: _ReqRefType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Downstream.ReqRef` instance with related information.

                :param req_ref: Starting requirement reference.
                """
                #: Starting requirement reference, verified by scenarios or not.
                self.req_ref = req_ref  # type: _ReqRefType
                #: Scenarios verifying this requirement reference.
                self.scenarios = []  # type: typing.List[ReqTraceability.Downstream.Scenario]

            def tojson(
                    self,
                    *,
                    allow_results,  # type: bool
            ):  # type: (...) -> _JsonDictType
                """
                Downstream traceability JSON content generation for this requirement reference.

                :param allow_results: ``False`` to prevent test results in the JSON content generated.
                :return: Downstream traceability JSON content.
                """
                _json_req_ref = {
                    "id": self.req_ref.id,
                    "scenarios": {},
                }  # type: _JsonDictType

                if self.req_ref.ismain():
                    if self.req_ref.req.title:
                        _json_req_ref["title"] = self.req_ref.req.title
                    if self.req_ref.req.text:
                        _json_req_ref["text"] = self.req_ref.req.text

                for _downstream_scenario in self.scenarios:  # type: ReqTraceability.Downstream.Scenario
                    _json_req_ref["scenarios"][_downstream_scenario.scenario.name] = _downstream_scenario.tojson(allow_results=allow_results)

                return _json_req_ref

        class Scenario:
            """
            Scenario verifying a :class:`ReqTraceability.Downstream.ReqRef`.

            .. note::
                Several instances of :class:`ReqTraceability.Downstream.Scenario` may exist for a single :class:`._scenariodefinition.ScenarioDefinition`.
                One for each requirement reference verified by the scenario (directly or through one of the scenario steps).
            """

            def __init__(
                    self,
                    downstream_req_ref,  # type: ReqTraceability.Downstream.ReqRef
                    scenario,  # type: _ScenarioDefinitionType
                    req_link,  # type: typing.Optional[_ReqLinkType]
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Downstream.Scenario` instance with related information.

                :param downstream_req_ref:
                    Requirement reference verified.
                :param scenario:
                    Scenario definition.
                :param req_link:
                    Related requirement link.

                    May be ``None`` when the requirement reference is verified indirectly through steps only.
                """
                #: Requirement reference verified by the scenario.
                self.downstream_req_ref = downstream_req_ref  # type: ReqTraceability.Downstream.ReqRef
                #: Scenario verifying the given requirement reference.
                self.scenario = scenario  # type: _ScenarioDefinitionType
                #: Optional direct link between the scenario and the requirement reference.
                #:
                #: May be ``None`` when the scenario verifies the requirement reference through one of its steps only.
                self.req_link = req_link  # type: typing.Optional[_ReqLinkType]
                #: Comments attached with this link.
                #:
                #: Empty when :attr:`req_link` is ``None``.
                #:
                #: When the link does not define an explicit comment, the scenario title is taken into account by default.
                self.comments = ""  # type: str
                #: Steps owned by the scenario, and verifying the given requirement reference.
                self.steps = []  # type: typing.List[ReqTraceability.Downstream.Step]

                if req_link:
                    self.comments = req_link.comments or scenario.title

                self.downstream_req_ref.scenarios.append(self)

            def tojson(
                    self,
                    *,
                    allow_results,  # type: bool
            ):  # type: (...) -> _JsonDictType
                """
                Downstream traceability JSON content generation for this scenario.

                :param allow_results: ``False`` to prevent test results in the JSON content generated.
                :return: Downstream traceability JSON content.
                """
                _json_scenario = {
                    "name": self.scenario.name,
                    "comments": self.comments,
                    "steps": {},
                }  # type: _JsonDictType

                if self.scenario.title:
                    _json_scenario["title"] = self.scenario.title

                if allow_results and (self.scenario.execution is not None):
                    _json_scenario["results"] = {
                        "status": str(self.scenario.execution.status),
                        "errors": [str(_error) for _error in self.scenario.execution.errors],
                        "warnings": [str(_warning) for _warning in self.scenario.execution.warnings],
                    }

                for _downstream_step in self.steps:  # type: ReqTraceability.Downstream.Step
                    _json_scenario["steps"][f"step#{_downstream_step.step.number}"] = _downstream_step.tojson(allow_results=allow_results)

                return _json_scenario

        class Step:
            """
            Scenario verifying an initial :class:`ReqTraceability.Downstream.ReqRef`.

            .. note::
                Several instances of :class:`ReqTraceability.Downstream.Step` may exist for a single :class:`._stepdefinition.StepDefinition`.
                One for each requirement reference verified by the step.
            """

            def __init__(
                    self,
                    downstream_scenario,  # type: ReqTraceability.Downstream.Scenario
                    step,  # type: _StepDefinitionType
                    req_link,  # type: _ReqLinkType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Downstream.Step` instance with related information.

                :param downstream_scenario: Owner scenario.
                :param step: Step definition.
                :param req_link: Related requirement link.
                """
                #: Scenario owning this step.
                self.downstream_scenario = downstream_scenario  # type: ReqTraceability.Downstream.Scenario
                #: Step verifying the requirement reference verified by :attr:`downstream_scenario`.
                self.step = step  # type: _StepDefinitionType
                #: Link between the step and the requirement reference.
                self.req_link = req_link  # type: _ReqLinkType
                #: Comments attached with this link.
                #:
                #: When the link does not define an explicit comment, the owner scenario title is taken into account by default.
                self.comments = req_link.comments or self.downstream_scenario.scenario.title  # type: str

                self.downstream_scenario.steps.append(self)

            def tojson(
                    self,
                    *,
                    allow_results,  # type: bool
            ):  # type: (...) -> _JsonDictType
                """
                Downstream traceability JSON content generation for this step.

                :param allow_results: ``False`` to prevent test results in the JSON content generated.
                :return: Downstream traceability JSON content.
                """
                from ._stepexecution import StepExecution

                _json_step = {
                    "number": self.step.number,
                    "name": self.step.name,
                    "comments": self.comments,
                }  # type: _JsonDictType

                # Note:
                #  Don't generate test results for an empty step execution list
                #  if the scenario has not been executed at all.
                if allow_results and (self.step.scenario.execution is not None):
                    _json_step["results"] = []
                    for _step_execution in self.step.executions:  # type: StepExecution
                        _json_step["results"].append({
                            "status": str(_step_execution.status),
                            "errors": [str(_error) for _error in _step_execution.errors],
                            "warnings": [str(_warning) for _warning in _step_execution.warnings],
                        })

                return _json_step

    def getdownstream(self):  # type: (...) -> ReqDownstreamTraceabilityType
        """
        Computes downstream traceability from data previously loaded with :meth:`loaddatafromfiles()` or :meth:`loaddatafromcampaignresults()`.

        :return: Downstream traceability.
        """
        from ._reflection import qualname
        from ._reqdb import REQ_DB
        if typing.TYPE_CHECKING:
            from ._reqtypes import SetWithReqLinksType
        from ._reqverifier import ReqVerifier

        self.debug("ReqTraceability.getdownstream(): Computing downstream traceability from %d requirement references in database", len(REQ_DB.getallrefs()))
        _downstream_req_refs = []  # type: typing.List[ReqTraceability.Downstream.ReqRef]
        for _req_ref in REQ_DB.getallrefs():  # type: _ReqRefType
            _downstream_req_ref = ReqTraceability.Downstream.ReqRef(req_ref=_req_ref)  # type: ReqTraceability.Downstream.ReqRef
            _downstream_req_refs.append(_downstream_req_ref)

            _downstream_scenario = None  # type: typing.Optional[ReqTraceability.Downstream.Scenario]

            _req_verifiers_set = _req_ref.getverifiers()  # type: SetWithReqLinksType[ReqVerifier]
            for _req_verifier in ReqVerifier.orderedset(_req_verifiers_set):  # type: ReqVerifier
                for _req_link in _req_verifiers_set[_req_verifier]:  # type: _ReqLinkType
                    if isinstance(_req_verifier, _ScenarioDefinitionImpl):
                        if (not _downstream_scenario) or (_downstream_scenario.scenario is not _req_verifier):
                            _downstream_scenario = ReqTraceability.Downstream.Scenario(
                                _downstream_req_ref,  # Memo: `_downstream_scenario` automatically added to `_downstream_req_ref`.
                                scenario=_req_verifier, req_link=_req_link,
                            )
                        else:
                            self.debug(
                                f"{_req_ref!r} -> {_req_verifier!r} already known through {_downstream_scenario.req_link!r}, "
                                f"{_req_link!r} ignored"
                            )
                    elif isinstance(_req_verifier, _StepDefinitionImpl):
                        # Ensure the owner scenario is set.
                        if (not _downstream_scenario) or (_downstream_scenario.scenario is not _req_verifier.scenario):
                            _downstream_scenario = ReqTraceability.Downstream.Scenario(
                                _downstream_req_ref,  # Memo: `_downstream_scenario` automatically added to `_downstream_req_ref`.
                                scenario=_req_verifier.scenario, req_link=None,
                            )
                        _downstream_step = ReqTraceability.Downstream.Step(
                            _downstream_scenario,  # Memo: `_downstream_step` automatically added to `_downstream_scenario`.
                            step=_req_verifier, req_link=_req_link,
                        )  # type: ReqTraceability.Downstream.Step
                    else:
                        raise ValueError(f"Unexpected verifier {_req_verifier!r}")

        self.debug("ReqTraceability.downstream() -> %d %s objects", len(_downstream_req_refs), qualname(ReqTraceability.Downstream.ReqRef))
        return _downstream_req_refs

    def writedownstream(
            self,
            outfile,  # type: _PathType
            downstream_traceability=None,  # type: ReqDownstreamTraceabilityType
            *,
            log_info=True,  # type: bool
            allow_results=True,  # type: bool
    ):  # type: (...) -> None
        """
        Writes downstream tracebility to a file.

        :param outfile:
            Path of the file to write.
        :param downstream_traceability:
            Downtream traceability to save into a file.

            Automatically computed when not set.
        :param log_info:
            ``True`` (by default) to generate info logging.
        :param allow_results:
            ``False`` to prevent test results in the downstream traceability report.
        """
        from ._jsondictutils import JsonDict
        from ._loggermain import MAIN_LOGGER

        if log_info:
            MAIN_LOGGER.info(f"Saving downstream traceability in '{outfile}'")

        # Automatically compute upstream tracebility if needed.
        if downstream_traceability is None:
            downstream_traceability = self.getdownstream()

        JsonDict.writefile(
            # Build a JSON content from the computed traceability.
            schema_subpath=ReqTraceability.Downstream.JSON_SCHEMA_SUBPATH,
            content=ReqTraceability.Downstream.tojson(downstream_traceability, allow_results=allow_results),
            # Save it to the given outfile.
            output_path=outfile,
        )

    class Upstream(abc.ABC):
        """
        Classes that describe an upstream traceability.

        Upstream traceability is a matrix starting with scenarios, verifying requirements and/or subreferences.
        """

        #: JSON schema subpath from :attr:`._pkginfo.PackageInfo.repo_url`, for upstream traceability reports.
        JSON_SCHEMA_SUBPATH = "schemas/upstream-traceability.schema.json"  # type: str

        @staticmethod
        def tojson(
                upstream_traceability,  # type: ReqUpstreamTraceabilityType
        ):  # type: (...) -> _JsonDictType
            """
            JSON content generation for an upstream traceability.

            :param upstream_traceability: Upstream traceability to generate JSON content for.
            :return: Upstream traceability JSON content.
            """
            _json = {}  # type: _JsonDictType
            for _upstream_scenario in upstream_traceability:  # type: ReqTraceability.Upstream.Scenario
                _json[_upstream_scenario.scenario.name] = _upstream_scenario.tojson()
            return _json

        class Scenario:
            """
            Main entry for upstream traceability.
            """

            def __init__(
                    self,
                    scenario,  # type: _ScenarioDefinitionType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Upstream.Scenario` instance with related information.

                :param scenario: Starting scenario.
                """
                #: Starting scenario, verifying requirements or not.
                self.scenario = scenario  # type: _ScenarioDefinitionType
                #: Requirements verified by the scenario.
                self.reqs = []  # type: typing.List[ReqTraceability.Upstream.Req]

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for this scenario.

                :return: Upstream traceability JSON content.
                """
                _json_scenario = {
                    "name": self.scenario.name,
                    "reqs": {},
                }  # type: _JsonDictType

                if self.scenario.title:
                    _json_scenario["title"] = self.scenario.title

                for _upstream_req in self.reqs:  # type: ReqTraceability.Upstream.Req
                    _json_scenario["reqs"][_upstream_req.req.id] = _upstream_req.tojson()

                return _json_scenario

        class Req:
            """
            Requirement verified by a :class:`ReqTraceability.Upstream.Scenario`.

            Either directly, or through the scenario steps.

            .. note::
                Several instances of :class:`ReqTraceability.Upstream.Req` may exist for a single :class:`._req.Req`.
                One for each scenario verifying the requirement (directly or through one of the requirement subreferences).
            """

            def __init__(
                    self,
                    upstream_scenario,  # type: ReqTraceability.Upstream.Scenario
                    req,  # type: _ReqType
                    req_link,  # type: typing.Optional[_ReqLinkType]
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Upstream.Req` instance with related information.

                :param upstream_scenario:
                    Scenario verifynig this requirement.
                :param req:
                    Requirement.
                :param req_link:
                    Related requirement link.

                    May be ``None`` when the verifies subreferences of the requirement only, but not the main part.
                """
                #: Scenario verifying the requirement.
                self.upstream_scenario = upstream_scenario  # type: ReqTraceability.Upstream.Scenario
                #: Requirement (main part) verified by the scenario.
                self.req = req  # type: _ReqType
                #: Optional direct link between the scenario (or one of its steps) and the requirement.
                #:
                #: May be ``None`` when the scenario verifies subreferences only, but not the main part of the requirement.
                self.req_link = req_link  # type: typing.Optional[_ReqLinkType]
                #: Comments attached with this link.
                #:
                #: Empty when :attr:`req_link` is ``None``.
                #:
                #: When the link does not define an explicit comment, the scenario title is taken into account by default.
                self.comments = ""  # type: str
                #: Subreferences of the requirement, verified by the given scenario.
                self.req_subrefs = []  # type: typing.List[ReqTraceability.Upstream.ReqSubref]

                if req_link:
                    self.comments = req_link.comments or self.upstream_scenario.scenario.title

                self.upstream_scenario.reqs.append(self)

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for this requirement.

                :return: Upstream traceability JSON content.
                """
                _json_req = {
                    "id": self.req.id,
                    "comments": self.comments,
                    "subrefs": {},
                }  # type: _JsonDictType

                if self.req.title:
                    _json_req["title"] = self.req.title
                # Don't repeat text with requirements in upstream traceability reports.
                # if self.req.text:
                #     _json_req["text"] = self.req.text

                for _upstream_req_subref in self.req_subrefs:  # type: ReqTraceability.Upstream.ReqSubref
                    _json_req["subrefs"][_upstream_req_subref.req_subref.id] = _upstream_req_subref.tojson()

                return _json_req

        class ReqSubref:
            """
            Requirement subreference verified by an initial :class:`ReqTraceability.Upstream.Scenario`.

            .. note::
                Several instances of :class:`ReqTraceability.Upstream.ReqSubref` may exist for a single :class:`._reqref.ReqRef`.
                One for each scenario verifying the requirement subreference.
            """

            def __init__(
                    self,
                    upstream_req,  # type: ReqTraceability.Upstream.Req
                    req_subref,  # type: _ReqRefType
                    req_link,  # type: _ReqLinkType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Upstream.ReqSubref` instance with related information.

                :param upstream_req: Owner requirement.
                :param req_subref: Requirement subreference.
                :param req_link: Related requirement link.
                """
                #: Requirement owning this subreference.
                self.upstream_req = upstream_req  # type: ReqTraceability.Upstream.Req
                if not req_subref.issubref():
                    raise ValueError(f"Invalid requirement subreference {req_subref!r}")
                #: Requirement subreference verified by the scenario verifying :attr:`upstream_req`.
                self.req_subref = req_subref  # type: _ReqRefType
                #: Link between the scenario (or one of its steps) and the requirement subreference.
                self.req_link = req_link  # type: _ReqLinkType
                #: Comments attached with this link.
                #:
                #: When the link does not define an explicit comment, the scenario title is taken into account by default.
                self.comments = req_link.comments or self.upstream_req.upstream_scenario.scenario.title  # type: str

                self.upstream_req.req_subrefs.append(self)

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for this requirement subreference.

                :return: Upstream traceability JSON content.
                """
                return {
                    "id": self.req_subref.id,
                    "comments": self.comments,
                }

    def getupstream(self):  # type: (...) -> ReqUpstreamTraceabilityType
        """
        Computes upstream traceability from data previously loaded with :meth:`loaddatafromfiles()` or :meth:`loaddatafromcampaignresults()`.

        :return: Upstream traceability.
        """
        from ._reflection import qualname
        if typing.TYPE_CHECKING:
            from ._reqtypes import SetWithReqLinksType

        self.debug("ReqTraceability.upstream(): Computing upstream traceability from %d loaded scenarios", len(self.scenarios))
        _upstream_scenarios = []  # type: typing.List[ReqTraceability.Upstream.Scenario]
        for _scenario in self.scenarios:  # type: _ScenarioDefinitionType
            _upstream_scenario = ReqTraceability.Upstream.Scenario(scenario=_scenario)  # type: ReqTraceability.Upstream.Scenario
            _upstream_scenarios.append(_upstream_scenario)

            _upstream_req = None  # type: typing.Optional[ReqTraceability.Upstream.Req]

            _req_ref_set = _scenario.getreqrefs(walk_steps=True)  # type: SetWithReqLinksType[_ReqRefType]
            for _req_ref in _ReqRefImpl.orderedset(_req_ref_set):  # type: _ReqRefType
                for _req_link in _req_ref_set[_req_ref]:  # type: _ReqLinkType
                    if _req_ref.ismain():
                        if (not _upstream_req) or (_upstream_req.req is not _req_ref.req):
                            _upstream_req = ReqTraceability.Upstream.Req(
                                _upstream_scenario,  # Memo: `_upstream_req` automatically added to `_upstream_scenario`.
                                req=_req_ref.req, req_link=_req_link,
                            )
                        else:
                            self.debug(
                                "%s -> %s already known through [%s], [%s] ignored",
                                _scenario, _req_ref.req, _upstream_req.req_link, _req_link,
                            )
                    else:
                        # Ensure the main requirement is set.
                        if (not _upstream_req) or (_upstream_req.req is not _req_ref.req):
                            _upstream_req = ReqTraceability.Upstream.Req(
                                _upstream_scenario,  # Memo: `_upstream_req` automatically added to `_upstream_scenario`.
                                req=_req_ref.req, req_link=None,
                            )
                        _upstream_req_subref = ReqTraceability.Upstream.ReqSubref(
                            _upstream_req,  # Memo: `_upstream_req_subref` automatically added to `_upstream_req`.
                            req_subref=_req_ref, req_link=_req_link,
                        )  # type: ReqTraceability.Upstream.ReqSubref

        self.debug("ReqTraceability.upstream() -> %d %s objects", len(_upstream_scenarios), qualname(ReqTraceability.Upstream.Scenario))
        return _upstream_scenarios

    def writeupstream(
            self,
            outfile,  # type: _PathType
            upstream_traceability=None,  # type: ReqUpstreamTraceabilityType
            *,
            log_info=True,  # type: bool
    ):  # type: (...) -> None
        """
        Writes upstream tracebility to a file.

        :param outfile:
            Path of the file to write.
        :param upstream_traceability:
            Upstream traceability to save into a file.

            Automatically computed when not set.
        :param log_info:
            ``True`` (by default) to generate info logging.
        """
        from ._jsondictutils import JsonDict
        from ._loggermain import MAIN_LOGGER

        if log_info:
            MAIN_LOGGER.info(f"Saving upstream traceability in '{outfile}'")

        # Automatically compute upstream tracebility if needed.
        if upstream_traceability is None:
            upstream_traceability = self.getupstream()

        JsonDict.writefile(
            # Build a JSON content from the computed traceability.
            schema_subpath=ReqTraceability.Upstream.JSON_SCHEMA_SUBPATH,
            content=ReqTraceability.Upstream.tojson(upstream_traceability),
            # Save it to the given outfile.
            output_path=outfile,
        )


if typing.TYPE_CHECKING:
    #: Downstream traceability type.
    #:
    #: Sequence of :class:`ReqTraceability.Downstream.ReqRef` instances,
    #: each owning a sequence of :class:`ReqTraceability.Downstream.Scenario` instances,
    #: each possibly owning :class:`ReqTraceability.Downstream.Step` instances.
    ReqDownstreamTraceabilityType = typing.Sequence[ReqTraceability.Downstream.ReqRef]

    #: Upstream traceability type.
    #:
    #: Sequence of :class:`ReqTracibility.Upstream.Scenario` instances,
    #: each owning a sequence of :class:`ReqTraceability.Upstream.Req` instances,
    #: each possibly owning :class:`ReqTraceability.Upstream.ReqSubref` instances.
    ReqUpstreamTraceabilityType = typing.Sequence[ReqTraceability.Upstream.Scenario]


#: Main instance of :class:`ReqTraceability`.
REQ_TRACEABILITY = ReqTraceability()  # type: ReqTraceability
