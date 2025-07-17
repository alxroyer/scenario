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
    from ._debugclasses import DebugClass as _DebugClassImpl  # @perf
    from ._fastpath import FAST_PATH as _FAST_PATH  # @perf
    from ._logger import Logger as _LoggerImpl  # @inheritance
    from ._reqblobj import ReqBaselineObject as _ReqBaselineObjectImpl  # @inheritance
    from ._reqref import ReqRef as _ReqRefImpl  # @perf
    from ._reqverifier import ReqVerifier as _ReqVerifierImpl  # @perf
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionImpl  # @perf
    from ._stepdefinition import StepDefinition as _StepDefinitionImpl  # @perf
if typing.TYPE_CHECKING:
    from ._jsondictutils import JsonDictType as _JsonDictType
    from ._path import Path as _PathType
    from ._req import Req as _ReqType
    from ._reqbl import ReqBaseline as _ReqBaselineType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._stepdefinition import StepDefinition as _StepDefinitionType
    from ._stepexecution import StepExecution as _StepExecutionType


class ReqTraceability(_LoggerImpl, _ReqBaselineObjectImpl):
    """
    Requirement traceability computation.
    """

    def __init__(
            self,
            req_baseline,  # type: _ReqBaselineType
    ):  # type: (...) -> None
        """
        Stores the related baseline reference and configures logging for :class:`ReqTraceability`.

        :param req_baseline: Requirement baseline to compute traceability for.
        """
        _LoggerImpl.__init__(self, _DebugClassImpl.REQ_TRACEABILITY)
        _ReqBaselineObjectImpl.__init__(self, req_baseline)

    class Downstream(abc.ABC):
        """
        Classes that describe a downstream traceability.

        Downstream traceability is a matrix starting with requirement references, verified by scenarios and steps.
        """

        #: JSON schema subpath from :attr:`._pkginfo.PackageInfo.repo_url`, for downstream traceability reports.
        JSON_SCHEMA_SUBPATH = "schemas/downstream-traceability_v0.3.0.schema.json"  # type: str

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
            from ._jsondictutils import JsonDict

            _json = {}  # type: _JsonDictType
            for _downstream_req in downstream_traceability:  # type: ReqTraceability.Downstream.Req
                JsonDict.Build.addentry(
                    _json,
                    id=_downstream_req.req.id,
                    entry=_downstream_req.tojson(allow_results=allow_results),
                    redundant_fields=ReqTraceabilityHelper.redundant_fields(_downstream_req),
                )
            return _json

        class Req:
            """
            Main entry for downstream traceability, one for each main requirement.
            """

            def __init__(
                    self,
                    req,  # type: _ReqType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Downstream.Req` instance with related information.

                :param req: Starting main requirement reference.
                """
                #: Main requirement, verified by scenarios or not.
                self.req = req  # type: _ReqType
                #: Subreferences of this main requirement, verified by scenarios or not.
                self.subrefs = []  # type: typing.List[ReqTraceability.Downstream.Subref]
                #: Scenarios verifying this main requirement.
                self.scenarios = []  # type: typing.List[ReqTraceability.Downstream.Scenario]

            @property
            def req_ref(self):  # type: () -> _ReqRefType
                """
                Starting main requirement reference, as a generic :class:`._reqref.ReqRef`.
                """
                return self.req.main_ref

            def tojson(
                    self,
                    *,
                    allow_results,  # type: bool
            ):  # type: (...) -> _JsonDictType
                """
                Downstream traceability JSON content generation for the main requirement.

                :param allow_results: ``False`` to prevent test results in the JSON content generated.
                :return: Downstream traceability JSON content.
                """
                from ._jsondictutils import JsonDict

                _json_req = {
                    "id": self.req_ref.id,
                    "title": self.req.title,
                    "text": self.req.text,
                    "subrefs": {},
                    "scenarios": {},
                }  # type: _JsonDictType

                for _downstream_subref in self.subrefs:  # type: ReqTraceability.Downstream.Subref
                    JsonDict.Build.addentry(
                        _json_req["subrefs"],
                        id=_downstream_subref.subref.id,
                        entry=_downstream_subref.tojson(allow_results=allow_results),
                        redundant_fields=ReqTraceabilityHelper.redundant_fields(_downstream_subref),
                    )

                for _downstream_scenario in self.scenarios:  # type: ReqTraceability.Downstream.Scenario
                    JsonDict.Build.addentry(
                        _json_req["scenarios"],
                        id=_downstream_scenario.id,
                        entry=_downstream_scenario.tojson(allow_results=allow_results),
                        redundant_fields=ReqTraceabilityHelper.redundant_fields(_downstream_scenario),
                    )

                JsonDict.Build.removeemptyfields(
                    _json_req,
                    ["title", "text", "subrefs"],  # Let empty "scenarios" lists.
                )

                return _json_req

        class Subref:
            """
            Requirement subreference subentry for downstream traceability.

            Stored in the related :class:`ReqTraceability.Downstream.Req` main entry.
            """

            def __init__(
                    self,
                    downstream_req,  # type: ReqTraceability.Downstream.Req
                    subref,  # type: _ReqRefType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Downstream.Subref` instance with related information.

                :param downstream_req: Related main requirement.
                :param subref: Requirement subreference.

                Automatically adds the new subreference to the related ``downstream_req``.
                """
                #: Related main requirement.
                self.downstream_req = downstream_req  # type: ReqTraceability.Downstream.Req
                #: Requirement subreference, verified by scenarios or not.
                self.subref = subref  # type: _ReqRefType
                #: Scenarios verifying this requirement subreference.
                self.scenarios = []  # type: typing.List[ReqTraceability.Downstream.Scenario]

                # Automatically add this new subreference to the related requirement.
                self.downstream_req.subrefs.append(self)

            @property
            def req_ref(self):  # type: () -> _ReqRefType
                """
                Requirement subreference, as a generic :class:`._reqref.ReqRef`.
                """
                return self.subref

            def tojson(
                    self,
                    *,
                    allow_results,  # type: bool
            ):  # type: (...) -> _JsonDictType
                """
                Downstream traceability JSON content generation for the requirement subreference.

                :param allow_results: ``False`` to prevent test results in the JSON content generated.
                :return: Downstream traceability JSON content.
                """
                from ._jsondictutils import JsonDict

                _json_subref = {
                    "id": self.subref.id,
                    # Save title for consistency with `Upstream.Subref.tojson()`.
                    "title": self.subref.title,
                    "scenarios": {},
                }  # type: _JsonDictType

                for _downstream_scenario in self.scenarios:  # type: ReqTraceability.Downstream.Scenario
                    JsonDict.Build.addentry(
                        _json_subref["scenarios"],
                        id=_downstream_scenario.id,
                        entry=_downstream_scenario.tojson(allow_results=allow_results),
                        redundant_fields=ReqTraceabilityHelper.redundant_fields(_downstream_scenario),
                    )

                # Remove optional information when empty.
                JsonDict.Build.removeemptyfields(
                    _json_subref,
                    ["title"],  # Let empty "scenarios" lists.
                )

                return _json_subref

        if typing.TYPE_CHECKING:
            #: Generic type for :class:`ReqTraceability.Downstream.Req` and :class:`ReqTraceability.Downstream.Subref` classes.
            ReqRefType = typing.Union[Req, Subref]

        class Scenario:
            """
            Scenario verifying a :obj:`ReqTraceability.Downstream.ReqRefType`.

            .. note::
                Several instances of :class:`ReqTraceability.Downstream.Scenario` may exist for a single :class:`._scenariodefinition.ScenarioDefinition`.
                One for each requirement reference verified by the scenario (directly or through one of the scenario steps).
            """

            def __init__(
                    self,
                    downstream_req_ref,  # type: ReqTraceability.Downstream.ReqRefType
                    scenario,  # type: _ScenarioDefinitionType
                    req_link,  # type: typing.Optional[_ReqLinkType]
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Downstream.Scenario` instance with related information.

                :param downstream_req_ref:
                    Requirement reference verified.
                    Either a main requirement or a subreference.
                :param scenario:
                    Scenario definition.
                :param req_link:
                    Related requirement link.

                    May be ``None`` when the requirement reference is verified indirectly through steps only.

                Automatically add the new scenario to the related ``downstream_req_ref``.
                """
                #: Requirement reference verified by the scenario.
                self.downstream_req_ref = downstream_req_ref  # type: ReqTraceability.Downstream.ReqRefType
                #: Scenario verifying the given requirement reference.
                self.scenario = scenario  # type: _ScenarioDefinitionType
                #: Optional direct link between the scenario and the requirement reference.
                #:
                #: May be ``None`` when the scenario verifies the requirement reference through one of its steps only.
                self.req_link = req_link  # type: typing.Optional[_ReqLinkType]
                #: Steps owned by the scenario, and verifying the given requirement reference.
                self.steps = []  # type: typing.List[ReqTraceability.Downstream.Step]

                # Automatically add this new scenario to the related requirement reference.
                self.downstream_req_ref.scenarios.append(self)

            @property
            def id(self):  # type: () -> str
                """
                Scenario identifier in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkscenarioid()`
                """
                return ReqTraceabilityHelper.mkscenarioid(self.scenario)

            @property
            def name(self):  # type: () -> str
                """
                Scenario display name in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkscenarioid()`
                """
                return ReqTraceabilityHelper.mkscenarioname(self.scenario)

            @property
            def explicit_comments(self):  # type: () -> str
                """
                Explicit requirement coverage comments, if defined by the requirement link.
                """
                if self.req_link:
                    return self.req_link.comments
                return ""

            @property
            def display_comments(self):  # type: () -> str
                """
                Comments explaining the requirement coverage made by this scenario.

                Empty when no requirement link is provided,
                to let steps explain the requirement coverage.

                When the requirement link provided does not define explicit comments,
                the scenario title is taken into account by default.
                """
                # Let steps explain the coverage when no requirement link is provided.
                if self.req_link is None:
                    return ""

                # Explicit comments if provided.
                if self.req_link.comments:
                    return self.req_link.comments

                # Default to scenario title.
                return self.scenario.title

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
                from ._jsondictutils import JsonDict

                _json_scenario = {
                    "id": self.id,
                    "name": self.name,
                    "title": self.scenario.title,
                    "comments": self.explicit_comments,
                    "steps": {},
                }  # type: _JsonDictType

                if allow_results and (self.scenario.execution is not None):
                    _json_scenario["results"] = {
                        "status": str(self.scenario.execution.status),
                        "errors": [_error.tojson() for _error in self.scenario.execution.errors],
                        "warnings": [_warning.tojson() for _warning in self.scenario.execution.warnings],
                    }

                for _downstream_step in self.steps:  # type: ReqTraceability.Downstream.Step
                    JsonDict.Build.addentry(
                        _json_scenario["steps"],
                        id=_downstream_step.short_id,
                        entry=_downstream_step.tojson(allow_results=allow_results),
                        redundant_fields=ReqTraceabilityHelper.redundant_fields(_downstream_step),
                    )

                # Remove optional information when empty.
                JsonDict.Build.removeemptyfields(
                    _json_scenario,
                    ["title", "comments", "steps"],
                )

                return _json_scenario

        class Step:
            """
            Step verifying a :obj:`ReqTraceability.Downstream.ReqRefType`.

            .. note::
                Several instances of :class:`ReqTraceability.Downstream.Step` for the same step
                may exist for a single main :class:`ReqTraceability.Downstream.Req` entry.
                One for each requirement reference of the same requirement (main and/or subreferences) verified by the step.
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

                Automatically adds the new step to the related ``downstream_scenario``.
                """
                #: Scenario owning this step.
                self.downstream_scenario = downstream_scenario  # type: ReqTraceability.Downstream.Scenario
                #: Step verifying the requirement reference verified by :attr:`downstream_scenario`.
                self.step = step  # type: _StepDefinitionType
                #: Link between the step and the requirement reference.
                self.req_link = req_link  # type: _ReqLinkType

                # Automatically add this new step to the related scenario.
                self.downstream_scenario.steps.append(self)

            @property
            def full_id(self):  # type: () -> str
                """
                Full identifier in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepfullid()`
                """
                return ReqTraceabilityHelper.mkstepfullid(self.step)

            @property
            def short_id(self):  # type: () -> str
                """
                Short identifier in traceability results.

                When already located from its owner scenario.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepshortid()`
                """
                return ReqTraceabilityHelper.mkstepshortid(self.step)

            @property
            def name(self):  # type: () -> str
                """
                Step display name in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepname()`
                """
                return ReqTraceabilityHelper.mkstepname(self.step)

            @property
            def downstream_req_ref(self):  # type: () -> ReqTraceability.Downstream.ReqRefType
                """
                Requirement reference verified by the step.
                """
                return self.downstream_scenario.downstream_req_ref

            @property
            def explicit_comments(self):  # type: () -> str
                """
                Explicit requirement coverage comments, if defined by the requirement link.
                """
                return self.req_link.comments

            @property
            def display_comments(self):  # type: () -> str
                """
                Comments explaining the requirement coverage made by this step.

                When the requirement link does not define explicit comments,
                the owner scenario title and/or step description are taken into account by default.
                """
                # Explicit comments if provided.
                if self.req_link.comments:
                    return self.req_link.comments

                # Compute default comments from scenario title and/or step description.
                _comments = []  # type: typing.List[str]
                if self.downstream_scenario.scenario.title:
                    _comments.append(self.downstream_scenario.scenario.title)
                if self.step.description:
                    _comments.append(self.step.description)
                return " - ".join(_comments)

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
                from ._jsondictutils import JsonDict

                _json_step = {
                    "id": self.full_id,
                    "name": self.name,
                    "location": self.step.location.tolongstring(),
                    "description": self.step.description,
                    "comments": self.explicit_comments,
                }  # type: _JsonDictType

                # Note:
                #  Don't generate test results for an empty step execution list
                #  if the scenario has not been executed at all.
                if allow_results and (self.step.scenario.execution is not None):
                    _json_step["results"] = []
                    for _step_execution in self.step.executions:  # type: _StepExecutionType
                        _json_step["results"].append({
                            "status": str(_step_execution.status),
                            "errors": [_error.tojson() for _error in _step_execution.errors],
                            "warnings": [_warning.tojson() for _warning in _step_execution.warnings],
                        })

                # Remove optional information when empty.
                JsonDict.Build.removeemptyfields(
                    _json_step,
                    ["description", "comments"],
                )

                return _json_step

        if typing.TYPE_CHECKING:
            #: Generic type for :class:`ReqTraceability.Downstream.Scenario` and :class:`ReqTraceability.Downstream.Step` classes.
            ReqVerifierType = typing.Union[Scenario, Step]

    def getdownstream(
            self,
            *,
            walk_subrefs,  # type: bool
    ):  # type: (...) -> ReqDownstreamTraceabilityType
        """
        Computes downstream traceability from the related baseline.

        :param walk_subrefs:
            ``True`` to include subreference verifiers for main requirements.
        :return:
            Downstream traceability.

            Main and subreference requirement entries given whatever they are verified or not.
        """
        if typing.TYPE_CHECKING:
            from ._reqtypes import SetWithReqLinksType

        def _feedreqrefverifiers(
                downstream_req_ref,  # type: typing.Union[ReqTraceability.Downstream.Req, ReqTraceability.Downstream.Subref]
                req_verifiers_set,  # type: SetWithReqLinksType[_ReqVerifierType]
        ):  # type: (...) -> None
            _downstream_scenario = None  # type: typing.Optional[ReqTraceability.Downstream.Scenario]

            for _req_verifier in _ReqVerifierImpl.orderedset(req_verifiers_set):  # type: _ReqVerifierType
                for _req_link in req_verifiers_set[_req_verifier]:  # type: _ReqLinkType
                    if isinstance(_req_verifier, _ScenarioDefinitionImpl):
                        if (not _downstream_scenario) or (_downstream_scenario.scenario is not _req_verifier):
                            _downstream_scenario = ReqTraceability.Downstream.Scenario(
                                downstream_req_ref,  # Memo: `_downstream_scenario` automatically added to `downstream_req_ref`.
                                scenario=_req_verifier, req_link=_req_link,
                            )
                        else:
                            self.debug(
                                "%r -> %r already known through %r, %r ignored",
                                downstream_req_ref.req_ref, _req_verifier, _downstream_scenario.req_link, _req_link,
                            )
                    elif isinstance(_req_verifier, _StepDefinitionImpl):
                        # Ensure the owner scenario is set.
                        if (not _downstream_scenario) or (_downstream_scenario.scenario is not _req_verifier.scenario):
                            _downstream_scenario = ReqTraceability.Downstream.Scenario(
                                downstream_req_ref,  # Memo: `_downstream_scenario` automatically added to `downstream_req_ref`.
                                scenario=_req_verifier.scenario, req_link=None,
                            )
                        _downstream_step = ReqTraceability.Downstream.Step(
                            _downstream_scenario,  # Memo: `_downstream_step` automatically added to `_downstream_scenario`.
                            step=_req_verifier, req_link=_req_link,
                        )  # type: ReqTraceability.Downstream.Step
                    else:
                        raise ValueError(f"Unexpected verifier {_req_verifier!r}")

        _all_reqs = self.req_db.getallreqs()  # type: typing.Sequence[_ReqType]
        self.debug("ReqTraceability.getdownstream(): Computing downstream traceability from %d main requirement references", len(_all_reqs))
        _downstream_reqs = []  # type: typing.List[ReqTraceability.Downstream.Req]
        for _req in _all_reqs:  # type: _ReqType
            _downstream_req = ReqTraceability.Downstream.Req(_req)  # type: ReqTraceability.Downstream.Req
            _feedreqrefverifiers(_downstream_req, _req.getverifiers(walk_subrefs=walk_subrefs))

            for _subref in _req.subrefs:  # type: _ReqRefType
                _downstream_subref = ReqTraceability.Downstream.Subref(
                    _downstream_req,  # Memo: `_downstream_subref` automatically added to `_downstream_req`.
                    _subref,
                )  # type: ReqTraceability.Downstream.Subref
                _feedreqrefverifiers(_downstream_subref, _subref.getverifiers())

            # Save requirement entry in any case, even though no downstream traceability information.
            _downstream_reqs.append(_downstream_req)

        self.debug("ReqTraceability.downstream() -> %d %s objects",
                   len(_downstream_reqs), _FAST_PATH.reflection.qualname(ReqTraceability.Downstream.Req))
        return _downstream_reqs

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

        if log_info:
            _FAST_PATH.main_logger.info(f"Saving downstream traceability in '{outfile}'")

        # Automatically compute upstream tracebility if needed.
        if downstream_traceability is None:
            downstream_traceability = self.getdownstream(walk_subrefs=False)

        JsonDict.File.write(
            # Build a JSON content from the computed traceability.
            schema_subpath=ReqTraceability.Downstream.JSON_SCHEMA_SUBPATH,
            content=ReqTraceability.Downstream.tojson(downstream_traceability, allow_results=allow_results),
            # Save it to the given outfile.
            output_path=outfile,
        )

    class Upstream(abc.ABC):
        """
        Classes that describe an upstream traceability.

        Upstream traceability is a matrix starting with scenarios and steps, verifying requirements and/or subreferences.
        """

        #: JSON schema subpath from :attr:`._pkginfo.PackageInfo.repo_url`, for upstream traceability reports.
        JSON_SCHEMA_SUBPATH = "schemas/upstream-traceability_v0.3.0.schema.json"  # type: str

        @staticmethod
        def tojson(
                upstream_traceability,  # type: ReqUpstreamTraceabilityType
        ):  # type: (...) -> _JsonDictType
            """
            JSON content generation for an upstream traceability.

            :param upstream_traceability: Upstream traceability to generate JSON content for.
            :return: Upstream traceability JSON content.
            """
            from ._jsondictutils import JsonDict

            _json = {}  # type: _JsonDictType
            for _upstream_scenario in upstream_traceability:  # type: ReqTraceability.Upstream.Scenario
                JsonDict.Build.addentry(
                    _json,
                    id=_upstream_scenario.id,
                    entry=_upstream_scenario.tojson(),
                    redundant_fields=ReqTraceabilityHelper.redundant_fields(_upstream_scenario),
                )
            return _json

        class Scenario:
            """
            Main entry for upstream traceability, one for each scenario.
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
                #: Steps of this class, when verifying requirements only.
                self.steps = []  # type: typing.List[ReqTraceability.Upstream.Step]
                #: Requirements verified by the scenario.
                self.reqs = []  # type: typing.List[ReqTraceability.Upstream.Req]

            @property
            def req_verifier(self):  # type: () -> _ScenarioDefinitionType
                """
                Scenario as a generic :class:`._reqverifier.ReqVerifier`.
                """
                return self.scenario

            @property
            def id(self):  # type: () -> str
                """
                Identifier in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkscenarioid()`
                """
                return ReqTraceabilityHelper.mkscenarioid(self.scenario)

            @property
            def name(self):  # type: () -> str
                """
                Display name in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkscenarioname()`
                """
                return ReqTraceabilityHelper.mkscenarioname(self.scenario)

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for the scenario.

                :return: Upstream traceability JSON content.
                """
                from ._jsondictutils import JsonDict

                _json_scenario = {
                    "id": self.id,
                    "name": self.name,
                    "title": self.scenario.title,
                    "description": self.scenario.description,
                    "steps": {},
                    "reqs": {},
                }  # type: _JsonDictType

                for _upstream_step in self.steps:  # type: ReqTraceability.Upstream.Step
                    JsonDict.Build.addentry(
                        _json_scenario["steps"],
                        id=_upstream_step.short_id,
                        entry=_upstream_step.tojson(),
                        redundant_fields=ReqTraceabilityHelper.redundant_fields(_upstream_step),
                    )

                for _upstream_req in self.reqs:  # type: ReqTraceability.Upstream.Req
                    JsonDict.Build.addentry(
                        _json_scenario["reqs"],
                        id=_upstream_req.req.id,
                        entry=_upstream_req.tojson(),
                        redundant_fields=ReqTraceabilityHelper.redundant_fields(_upstream_req),
                    )

                # Remove optional information when empty.
                JsonDict.Build.removeemptyfields(
                    _json_scenario,
                    ["title", "description", "steps"],  # Let empty "reqs" lists.
                )

                return _json_scenario

        class Step:
            """
            Step subentry for upstream traceability.

            Stored in the related :class:`ReqTraceability.Upstream.Scenario` main entry.
            """

            def __init__(
                    self,
                    upstream_scenario,  # type: ReqTraceability.Upstream.Scenario
                    step,  # type: _StepDefinitionType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Upstream.Step` instance with related information.

                :param upstream_scenario: Related scenario.
                :param step: Step verifying requirements.

                Automatically adds the new step to the related ``upstream_scenario``.
                """
                #: Related scenario.
                self.upstream_scenario = upstream_scenario  # type: ReqTraceability.Upstream.Scenario
                #: Step verifying requirements.
                self.step = step  # type: _StepDefinitionType
                #: Requirements verified by the step.
                self.reqs = []  # type: typing.List[ReqTraceability.Upstream.Req]

                # Automatically add this new step to the related scenario.
                self.upstream_scenario.steps.append(self)

            @property
            def req_verifier(self):  # type: () -> _StepDefinitionType
                """
                Step as a generic :class:`._reqverifier.ReqVerifier`.
                """
                return self.step

            @property
            def full_id(self):  # type: () -> str
                """
                Full identifier in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepfullid()`
                """
                return ReqTraceabilityHelper.mkstepfullid(self.step)

            @property
            def short_id(self):  # type: () -> str
                """
                Short identifier in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepshortid()`
                """
                return ReqTraceabilityHelper.mkstepshortid(self.step)

            @property
            def name(self):  # type: () -> str
                """
                Display name in traceability results.

                .. seealso:: :meth:`ReqTraceabilityHelper.mkstepname()`
                """
                return ReqTraceabilityHelper.mkstepname(self.step)

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for the step.

                :return: Upstream traceability JSON content.
                """
                from ._jsondictutils import JsonDict

                _json_step = {
                    "id": self.full_id,
                    "name": self.name,
                    "location": self.step.location.tolongstring(),
                    "description": self.step.description,
                    "reqs": {},
                }  # type: _JsonDictType

                for _upstream_req in self.reqs:  # type: ReqTraceability.Upstream.Req
                    JsonDict.Build.addentry(
                        _json_step["reqs"],
                        id=_upstream_req.req.id,
                        entry=_upstream_req.tojson(),
                        redundant_fields=ReqTraceabilityHelper.redundant_fields(_upstream_req),
                    )

                JsonDict.Build.removeemptyfields(
                    _json_step,
                    ["description"],  # Let empty "reqs" lists.
                )

                return _json_step

        if typing.TYPE_CHECKING:
            #: Generic type for :class:`ReqTraceability.Upstream.Scenario` and :class:`ReqTraceability.Upstream.Step` classes.
            ReqVerifierType = typing.Union[Scenario, Step]

        class Req:
            """
            Main requirement verified by a :obj:`ReqTraceability.Upstream.ReqVerifierType`.

            Either directly, or through scenario steps.

            .. note::
                Several instances of :class:`ReqTraceability.Upstream.Req` may exist for a single :class:`._req.Req`.
                One for each scenario verifying the requirement (directly or through one of the requirement subreferences).
            """

            def __init__(
                    self,
                    upstream_req_verifier,  # type: ReqTraceability.Upstream.ReqVerifierType
                    req,  # type: _ReqType
                    req_link,  # type: typing.Optional[_ReqLinkType]
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Upstream.Req` instance with related information.

                :param upstream_req_verifier:
                    Scenario or step verifying this requirement.
                :param req:
                    Requirement.
                :param req_link:
                    Related requirement link.

                    May be ``None`` when the verifies subreferences of the requirement only, but not the main part.

                Automatically adds the new requirement to the related ``upstream_req_verifier``.
                """
                #: Scenario or step verifying the requirement.
                self.upstream_req_verifier = upstream_req_verifier  # type: ReqTraceability.Upstream.ReqVerifierType
                #: Requirement (main part) verified by the scenario.
                self.req = req  # type: _ReqType
                #: Optional direct link between the scenario (or one of its steps) and the requirement.
                #:
                #: May be ``None`` when the scenario verifies subreferences only, but not the main part of the requirement.
                self.req_link = req_link  # type: typing.Optional[_ReqLinkType]
                #: Subreferences of the requirement, verified by the given scenario.
                self.subrefs = []  # type: typing.List[ReqTraceability.Upstream.Subref]

                # Automatically add this new requirement to the related verifier.
                self.upstream_req_verifier.reqs.append(self)

            @property
            def explicit_comments(self):  # type: () -> str
                """
                Explicit requirement coverage comments, if defined by the requirement link.
                """
                if self.req_link:
                    return self.req_link.comments
                return ""

            @property
            def display_comments(self):  # type: () -> str
                """
                Comments explaining the coverage of this requirement.

                Empty when no requirement link is provided,
                to let subrefs explain the requirement coverage.

                When the requirement link provided does not define explicit comments,
                the requirement title is taken into account by default.
                """
                # Let subrefs explain the coverage when no requirement link is provided.
                if self.req_link is None:
                    return ""

                # Explicit comments if provided.
                if self.req_link.comments:
                    return self.req_link.comments

                # Default to requirement title.
                return self.req.title

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for this requirement.

                :return: Upstream traceability JSON content.
                """
                from ._jsondictutils import JsonDict

                _json_req = {
                    "id": self.req.id,
                    "title": self.req.title,
                    # Don't repeat text with requirements in upstream traceability reports.
                    # "text": self.req.text,
                    "comments": self.explicit_comments,
                    "subrefs": {},
                }  # type: _JsonDictType

                for _upstream_subref in self.subrefs:  # type: ReqTraceability.Upstream.Subref
                    JsonDict.Build.addentry(
                        _json_req["subrefs"],
                        id=_upstream_subref.subref.id,
                        entry=_upstream_subref.tojson(),
                        redundant_fields=ReqTraceabilityHelper.redundant_fields(_upstream_subref),
                    )

                # Remove optional information when empty.
                JsonDict.Build.removeemptyfields(
                    _json_req,
                    ["title", "comments", "subrefs"],
                )

                return _json_req

        class Subref:
            """
            Requirement subreference verified by a :obj:`ReqTraceability.Upstream.ReqVerifierType`.

            .. note::
                Several instances of :class:`ReqTraceability.Upstream.Subref` for the same requirement subreference
                may exist for a single main :class:`ReqTraceability.Upstream.Scenario` entry.
                One for the scenario and each of its steps verifying the requirement subreference.
            """

            def __init__(
                    self,
                    upstream_req,  # type: ReqTraceability.Upstream.Req
                    subref,  # type: _ReqRefType
                    req_link,  # type: _ReqLinkType
            ):  # type: (...) -> None
                """
                Builds a :class:`ReqTraceability.Upstream.Subref` instance with related information.

                :param upstream_req: Owner requirement.
                :param subref: Requirement subreference.
                :param req_link: Related requirement link.

                Automatically adds the new subreference to the related ``upstream_req``.
                """
                #: Requirement owning this subreference.
                self.upstream_req = upstream_req  # type: ReqTraceability.Upstream.Req
                if not subref.issubref():
                    raise ValueError(f"Invalid requirement subreference {subref!r}")
                #: Requirement subreference verified by the scenario verifying :attr:`upstream_req`.
                self.subref = subref  # type: _ReqRefType
                #: Link between the scenario (or one of its steps) and the requirement subreference.
                self.req_link = req_link  # type: _ReqLinkType

                # Automatically add this new subreference to the related requirement.
                self.upstream_req.subrefs.append(self)

            @property
            def upstream_req_verifier(self):  # type: () -> ReqTraceability.Upstream.ReqVerifierType
                """
                Scenario or step verifying the requirement subreference.
                """
                return self.upstream_req.upstream_req_verifier

            @property
            def explicit_comments(self):  # type: () -> str
                """
                Explicit requirement subref coverage comments, if defined by the requirement link.
                """
                return self.req_link.comments

            @property
            def display_comments(self):  # type: () -> str
                """
                Comments explaining the coverage of this requirement subref.

                When the requirement link does not define explicit comments,
                the requirement subref title is taken into account by default.
                """
                # Explicit comments if provided.
                if self.req_link.comments:
                    return self.req_link.comments

                # Default to requirement subref title.
                return self.subref.title

            def tojson(self):  # type: (...) -> _JsonDictType
                """
                Upstream traceability JSON content generation for this requirement subreference.

                :return: Upstream traceability JSON content.
                """
                from ._jsondictutils import JsonDict

                _json_subref = {
                    "id": self.subref.id,
                    # In the future, requirement subrefs may hold their own title.
                    # Currently, title is just computed from the main requirement title.
                    # Whatever, let's save it in reports as is to avoid empty subref dictionaries.
                    "title": self.subref.title,
                    # Don't repeat text with requirement subreferences in upstream traceability reports.
                    # "text": self.subref.text,
                    "comments": self.explicit_comments,
                }  # type: _JsonDictType

                # Remove optional information when empty.
                JsonDict.Build.removeemptyfields(
                    _json_subref,
                    ["title", "comments"],
                )

                return _json_subref

        if typing.TYPE_CHECKING:
            #: Generic type for :class:`ReqTraceability.Upstream.Req` and :class:`ReqTraceability.Upstream.Subref` classes.
            ReqRefType = typing.Union[Req, Subref]

    def getupstream(
            self,
            *,
            walk_steps,  # type: bool
    ):  # type: (...) -> ReqUpstreamTraceabilityType
        """
        Computes upstream traceability for the related baseline.

        :param walk_steps:
            ``True`` to include step requirement references for scenarios.
        :return:
            Upstream traceability.

            Scenario entries given even when verifying no requirement.
            Step entries given only when verifying requirements.
        """
        if typing.TYPE_CHECKING:
            from ._reqtypes import SetWithReqLinksType

        self.debug("ReqTraceability.upstream(): Computing upstream traceability from %d scenarios", len(self.req_baseline.scenarios))

        def _feedreqverifiercoverage(
                upstream_req_verifier,  # type: ReqTraceability.Upstream.ReqVerifierType
                req_ref_set,  # type: SetWithReqLinksType[_ReqRefType]
        ):  # type: (...) -> None
            _upstream_req = None  # type: typing.Optional[ReqTraceability.Upstream.Req]

            for _req_ref in _ReqRefImpl.orderedset(req_ref_set):  # type: _ReqRefType
                for _req_link in req_ref_set[_req_ref]:  # type: _ReqLinkType
                    if _req_ref.ismain():
                        if (not _upstream_req) or (_upstream_req.req is not _req_ref.req):
                            _upstream_req = ReqTraceability.Upstream.Req(
                                upstream_req_verifier,  # Memo: `_upstream_req` automatically added to `upstream_req_verifier`.
                                req=_req_ref.req, req_link=_req_link,
                            )
                        else:
                            self.debug(
                                "%r -> %r already known through %r, %r ignored",
                                upstream_req_verifier.req_verifier, _req_ref.req, _upstream_req.req_link, _req_link,
                            )
                    else:
                        # Ensure the main requirement is set.
                        if (not _upstream_req) or (_upstream_req.req is not _req_ref.req):
                            _upstream_req = ReqTraceability.Upstream.Req(
                                upstream_req_verifier,  # Memo: `_upstream_req` automatically added to `_upstream_req_verifier`.
                                req=_req_ref.req, req_link=None,
                            )
                        _upstream_subref = ReqTraceability.Upstream.Subref(
                            _upstream_req,  # Memo: `_upstream_subref` automatically added to `_upstream_req`.
                            subref=_req_ref, req_link=_req_link,
                        )  # type: ReqTraceability.Upstream.Subref

        _upstream_scenarios = []  # type: typing.List[ReqTraceability.Upstream.Scenario]
        for _scenario in self.req_baseline.scenarios:  # type: _ScenarioDefinitionType
            _upstream_scenario = ReqTraceability.Upstream.Scenario(_scenario)  # type: ReqTraceability.Upstream.Scenario
            _feedreqverifiercoverage(_upstream_scenario, _scenario.getreqrefs(walk_steps=walk_steps))

            for _step in _scenario.steps:  # type: _StepDefinitionType
                _upstream_step = ReqTraceability.Upstream.Step(_upstream_scenario, _step)  # type: ReqTraceability.Upstream.Step
                _feedreqverifiercoverage(_upstream_step, _step.getreqrefs())

                # Avoid step entries without upstream traceability information.
                if not _upstream_step.reqs:
                    del _upstream_scenario.steps[-1]

            # Save scenario entry in any case, even though no upstream traceability information.
            _upstream_scenarios.append(_upstream_scenario)

        self.debug("ReqTraceability.upstream() -> %d %s objects",
                   len(_upstream_scenarios), _FAST_PATH.reflection.qualname(ReqTraceability.Upstream.Scenario))
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

        if log_info:
            _FAST_PATH.main_logger.info(f"Saving upstream traceability in '{outfile}'")

        # Automatically compute upstream tracebility if needed.
        if upstream_traceability is None:
            upstream_traceability = self.getupstream(walk_steps=False)

        JsonDict.File.write(
            # Build a JSON content from the computed traceability.
            schema_subpath=ReqTraceability.Upstream.JSON_SCHEMA_SUBPATH,
            content=ReqTraceability.Upstream.tojson(upstream_traceability),
            # Save it to the given outfile.
            output_path=outfile,
        )


if typing.TYPE_CHECKING:
    #: Downstream traceability type.
    #:
    #: Sequence of :class:`ReqTraceability.Downstream.Req` instances (main entries),
    #: each possibly owning :class:`ReqTraceability.Downstream.Subref` instances (subentries).
    #:
    #: Each entry and subentry above owning a sequence of :class:`ReqTraceability.Downstream.Scenario` instances,
    #: each possibly owning :class:`ReqTraceability.Downstream.Step` instances.
    ReqDownstreamTraceabilityType = typing.Sequence[ReqTraceability.Downstream.Req]

    #: Upstream traceability type.
    #:
    #: Sequence of :class:`ReqTraceability.Upstream.Scenario` instances (main entries),
    #: each possibly owning :class:`ReqTraceability.Upstream.Step` instances (subentries).
    #:
    #: Each entry and subentry above owning a sequence of :class:`ReqTraceability.Upstream.Req` instances,
    #: each possibly owning :class:`ReqTraceability.Upstream.Subref` instances.
    ReqUpstreamTraceabilityType = typing.Sequence[ReqTraceability.Upstream.Scenario]


class ReqTraceabilityHelper(abc.ABC):
    """
    Requirement traceability helper methods.

    Avoids the public exposition of methods for internal implementation only.
    """

    @staticmethod
    def mkscenarioid(
            scenario,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> str
        """
        Common implementation for :attr:`ReqTraceability.Downstream.Scenario.id` and :attr:`ReqTraceability.Upstream.Scenario.id` properties.

        Scenario name.

        :param scenario: Scenario definition to compute an identifier for.
        :return: Identifier for the scenario in tracebility results.
        """
        return scenario.name

    @staticmethod
    def mkscenarioname(
            scenario,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> str
        """
        Common implementation for :attr:`ReqTraceability.Downstream.Scenario.name` and :attr:`ReqTraceability.Upstream.Scenario.name` properties.

        Scenario name.

        :param scenario: Scenario definition to compute a name for.
        :return: Name for the scenario in tracebility results.
        """
        return scenario.name

    @staticmethod
    def mkstepfullid(
            step,  # type: _StepDefinitionType
    ):  # type: (...) -> str
        """
        Common implementation for :attr:`ReqTraceability.Downstream.Step.full_id` and :attr:`ReqTraceability.Upstream.Step.full_id` properties.

        "<scenario id>/<step short id>" pattern.

        :param step: Step definition to compute an identifier for.
        :return: Full identifier for the step in tracebility results.
        """
        return f"{ReqTraceabilityHelper.mkscenarioid(step.scenario)}/{ReqTraceabilityHelper.mkstepshortid(step)}"

    @staticmethod
    def mkstepshortid(
            step,  # type: _StepDefinitionType
    ):  # type: (...) -> str
        """
        Common implementation for :attr:`ReqTraceability.Downstream.Step.short_id` and :attr:`ReqTraceability.Upstream.Step.short_id` properties.

        "step#<number>" pattern.

        :param step: Step definition to compute an identifier for.
        :return: Short identifier for the step in tracebility results.
        """
        return f"step#{step.number}"

    @staticmethod
    def mkstepname(
            step,  # type: _StepDefinitionType
    ):  # type: (...) -> str
        """
        Common implementation for :attr:`ReqTraceability.Downstream.Step.name` and :attr:`ReqTraceability.Upstream.Step.name` properties.

        "step#<number> (<class>)" pattern.

        :param step: Step definition to compute a name for.
        :return: Name for the step in tracebility results.
        """
        return f"step#{step.number} ({step.name})"

    if typing.TYPE_CHECKING:
        #: Any traceability object type.
        AnyObjType = typing.Union[
            ReqTraceability.Downstream.ReqRefType, ReqTraceability.Downstream.ReqVerifierType,
            ReqTraceability.Upstream.ReqVerifierType, ReqTraceability.Upstream.ReqRefType,
        ]

    @staticmethod
    def redundant_fields(
            obj,  # type: ReqTraceabilityHelper.AnyObjType
    ):  # type: (...) -> typing.Sequence[str]
        """
        Sequence of redundant field names with the given ``obj`` identifier.

        :param obj: Object to return redundant field names for.
        :return: Redundant field names.
        """
        _redundant_fields = ["id"]  # type: typing.List[str]
        if isinstance(obj, (ReqTraceability.Downstream.Scenario, ReqTraceability.Upstream.Scenario)):
            _redundant_fields.append("name")
        return _redundant_fields
