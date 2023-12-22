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
User interface scenario details page.
"""

import typing

if True:
    from ._requesthandler import RequestHandler as _RequestHandlerImpl  # `RequestHandler` used for inheritance.
if typing.TYPE_CHECKING:
    from .._actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from .._reqref import ReqRef as _ReqRefType
    from .._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from .._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from .._stepdefinition import StepDefinition as _StepDefinitionType
    from ._htmldoc import HtmlDocument as _HtmlDocumentType
    from ._httprequest import HttpRequest as _HttpRequestType


class ScenarioDetails(_RequestHandlerImpl):
    """
    Scenario details page.
    """

    #: Base URL for the scenario details page.
    URL = "/scenario"

    @staticmethod
    def mkurl(
            req_verifier,  # type: typing.Union[_ScenarioDefinitionType, _StepDefinitionType]
    ):  # type: (...) -> str
        """
        Builds a scenario details URL for the given scenario.

        :param req_verifier: Scenario or step to build the URL for.
        :return: Scenario details URL for the given scenario.
        """
        from .._scenariodefinition import ScenarioDefinition
        from .._stepdefinition import StepDefinition
        from ._httprequest import HttpRequest

        _scenario = req_verifier if isinstance(req_verifier, ScenarioDefinition) else req_verifier.scenario  # type: ScenarioDefinition

        _step_anchor = None  # type: typing.Optional[str]
        if isinstance(req_verifier, StepDefinition):
            _step_anchor = f"step#{req_verifier.number}"

        return HttpRequest.encodeurl(ScenarioDetails.URL, args={'name': _scenario.name}, anchor=_step_anchor)

    def _getscenario(
            self,
            scenario_name,  # type: str
    ):  # type: (...) -> _ScenarioDefinitionType
        """
        Retrieves the scenario instance with details.

        Ensures steps are executed at once to build actions and expected results.

        :param scenario_name: Name of the scenario searched.
        :return: Scenario found from its name.
        """
        from .._reqtraceability import REQ_TRACEABILITY
        from .._scenarioexecution import ScenarioExecution
        from .._scenariostack import SCENARIO_STACK

        # Search for the scenario in the loaded scenarios.
        for _scenario_definition in REQ_TRACEABILITY.scenarios:  # type: _ScenarioDefinitionType
            if _scenario_definition.name == scenario_name:
                # Scenario found.
                if not _scenario_definition.execution:
                    # Load scenario details.
                    try:
                        # Prepare the scenario for working with `ScenarioRunner` and `ScenarioStack`.
                        _scenario_definition.execution = ScenarioExecution(_scenario_definition)
                        SCENARIO_STACK.building.pushscenariodefinition(_scenario_definition)

                        # Start iterating over the scenario steps.
                        _scenario_definition.execution.startsteplist()
                        while _scenario_definition.execution.current_step_definition:
                            # Execute the step in *building* mode.
                            _scenario_definition.execution.current_step_definition.step()

                            # Switch to the next step.
                            _scenario_definition.execution.nextstep()
                    finally:
                        SCENARIO_STACK.building.popscenariodefinition(_scenario_definition)
                return _scenario_definition
        raise KeyError(f"No such scenario {scenario_name!r}")

    def matches(
            self,
            request,  # type: _HttpRequestType
    ):  # type: (...) -> bool
        return request.base_path == ScenarioDetails.URL

    def process(
            self,
            request,  # type: _HttpRequestType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        # Retrieve the scenario name from request arguments.
        _scenario_name = request.getarg("name")  # type: str
        # Then find the scenario instance from the loaded scenarios.
        _scenario = self._getscenario(_scenario_name)  # type: _ScenarioDefinitionType

        # HTML content.
        html.settitle(_scenario.name)

        with html.addcontent('<div id="scenario"></div>'):
            if _scenario.getattributenames():
                self._scenarioattributes2html(_scenario, html)

            _req_refs = _scenario.getreqrefs(walk_steps=True)  # type: _SetWithReqLinksType[_ReqRefType]
            if _req_refs:
                self._reqrefs2html(_scenario, _req_refs, html)

            self._steps2html(_scenario, html)

    def _scenarioattributes2html(
            self,
            scenario,  # type: _ScenarioDefinitionType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for scenario attributes.

        :param scenario: Scenario which attributes to build HTML content for.
        :param html: HTML output page to feed.
        """
        with html.addcontent('<div class="scenario attributes"></div>'):
            html.addcontent('<p>Attributes:</p>')
            with html.addcontent('<ul></ul>'):
                for _attr_name in scenario.getattributenames():  # type: str
                    with html.addcontent('<li class="scenario attribute"></li>'):
                        html.addcontent(f'<span class="scenario attribute name">{html.encode(_attr_name)}</span>')
                        html.addcontent('<span class="scenario attribute sep">:</span>')
                        html.addcontent(f'<span class="scenario attribute value">{html.encode(scenario.getattribute(_attr_name))}</span>')

    def _steps2html(
            self,
            scenario,  # type: _ScenarioDefinitionType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for scenario steps.

        :param scenario: Scenario which steps to build HTML content for.
        :param html: HTML output page to feed.
        """
        with html.addcontent('<div id="steps"></div>'):
            html.addcontent('<p>Steps:</p>')
            with html.addcontent('<ul></ul>'):
                for _step in scenario.steps:  # type: _StepDefinitionType
                    self._step2html(_step, html)

    def _step2html(
            self,
            step,  # type: _StepDefinitionType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given step.

        :param step: Step to build HTML content for.
        :param html: HTML output page to feed.
        """
        from .._stepsection import StepSectionDescription

        with html.addcontent('<li class="step"></li>'):
            if isinstance(step, StepSectionDescription) and step.description:
                html.addcontent(f'<h2 class="step">{html.encode(step.description)}</h2>')
            else:
                # Step anchor.
                html.addcontent(f'<a name="step#{step.number}" />')

                # Step number, description and name.
                html.addcontent(f'<span class="step number">step#{step.number}</span>')
                if step.description:
                    html.addcontent('<span class="step sep">:</span>')
                    html.addcontent(f'<span class="step description">{step.description}</span>')
                html.addcontent(f'<span class="step name">({step.name})</span>')

                # Step requirements coverage.
                _req_refs = step.getreqrefs()  # type: _SetWithReqLinksType[_ReqRefType]
                if _req_refs:
                    self._reqrefs2html(step, _req_refs, html)

                # Actions & expected results.
                with html.addcontent(f'<div class="actions-results"></div>'):
                    with html.addcontent('<ul></ul>'):
                        for _action_result in step.actions_results:  # type: _ActionResultDefinitionType
                            self._actionresult2html(_action_result, html)

    def _actionresult2html(
            self,
            action_result,  # type: _ActionResultDefinitionType
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given action / expected result.

        :param action_result: Action / expected result to build HTML content for.
        :param html: HTML output page to feed.
        """
        with html.addcontent(f'<li class="{action_result.type.lower()}"></li>'):
            html.addcontent(f'<span class="{action_result.type.lower()} type">{action_result.type.upper()}</span>')
            html.addcontent(f'<span class="{action_result.type.lower()} sep">:</span>')
            html.addcontent(f'<span class="{action_result.type.lower()} text">{html.encode(action_result.description)}</span>')

    def _reqrefs2html(
            self,
            req_verifier,  # type: typing.Union[_ScenarioDefinitionType, _StepDefinitionType]
            req_refs,  # type: _SetWithReqLinksType[_ReqRefType]
            html,  # type: _HtmlDocumentType
    ):  # type: (...) -> None
        """
        Buils the HTML content for a scenario or step requirement coverage.

        :param req_verifier: Scenario or step to process requirement coverage for.
        :param req_refs: Scenario or step requirement coverage.
        :param html: HTML output page to feed.
        """
        from .._reqlink import ReqLink
        from .._scenariodefinition import ScenarioDefinition
        from .._stepdefinition import StepDefinition
        from ._downstreamtraceability import DownstreamTraceability
        from ._requirements import Requirements
        from ._upstreamtraceability import UpstreamTraceability

        # Determine the HTML object class depending on the type of `req_verifier`.
        _obj_class = ""  # type: str
        if isinstance(req_verifier, ScenarioDefinition):
            _obj_class = "scenario"
        if isinstance(req_verifier, StepDefinition):
            _obj_class = "step"

        with html.addcontent(f'<div class="{_obj_class} requirements"></div>'):
            html.addcontent('<p>Requirements:</p>')
            with html.addcontent('<ul></ul>'):
                for _req_ref in req_refs:  # type: _ReqRefType
                    with html.addcontent(f'<li class="{_obj_class} req-ref"></li>'):
                        # Requirement reference id.
                        with html.addcontent(f'<span class="{_obj_class} req-ref id"></span>'):
                            with html.addcontent(f'<a href="{Requirements.mkurl(_req_ref)}"></a>'):
                                html.addtext(_req_ref.id)

                        # Downstream traceability link.
                        with html.addcontent(f'<span class="{_obj_class} req-ref coverage"></span>'):
                            DownstreamTraceability.reqref2unnamedhtmllink(_req_ref, html)

                        # Find out the req-links which comments to display.
                        _req_links = list(filter(
                            # Filter on `obj` only.
                            lambda req_link: req_verifier in req_link.req_verifiers,
                            req_refs[_req_ref],
                        ))  # type: typing.Sequence[ReqLink]
                        # Determine the comments to display from the latter.
                        _comments = ', '.join(map(lambda req_link: req_link.comments, _req_links))  # type: str
                        if not _comments:
                            _comments = "(see steps)"

                        html.addcontent(f'<span class="{_obj_class} req-ref sep">:</span>')
                        html.addcontent(f'<span class="{_obj_class} req-ref comments">{html.encode(_comments)}</span>')

            # Upstream traceability link.
            if isinstance(req_verifier, ScenarioDefinition):
                UpstreamTraceability.scenario2unnamedhtmllink(req_verifier, html)
