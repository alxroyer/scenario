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
            scenario,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> str
        """
        Builds a scenario details URL for the given scenario.

        :param scenario: Scenario to build the URL for.
        :return: Scenario details URL for the given scenario.
        """
        from ._httprequest import HttpRequest

        return HttpRequest.encodeurl(ScenarioDetails.URL, {'name': scenario.name})

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
                self._scenarioattributes(html, _scenario)

            _req_refs = _scenario.getreqrefs(walk_steps=True)  # type: _SetWithReqLinksType[_ReqRefType]
            if _req_refs:
                self._reqrefs(html, _scenario, _req_refs)

            self._steps(html, _scenario)

    def _scenarioattributes(
            self,
            html,  # type: _HtmlDocumentType
            scenario,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> None
        """
        Builds the HTML content for scenario attributes.

        :param html: HTML output page to feed.
        :param scenario: Scenario which attributes to build HTML content for.
        """
        with html.addcontent('<div class="scenario attributes"></div>'):
            html.addcontent('<p>Attributes:</p>')
            with html.addcontent('<ul></ul>'):
                for _attr_name in scenario.getattributenames():  # type: str
                    with html.addcontent('<li class="scenario attribute"></li>'):
                        html.addcontent(f'<span class="scenario attribute name">{html.encode(_attr_name)}</span>')
                        html.addcontent('<span class="scenario attribute sep">:</span>')
                        html.addcontent(f'<span class="scenario attribute value">{html.encode(scenario.getattribute(_attr_name))}</span>')

    def _steps(
            self,
            html,  # type: _HtmlDocumentType
            scenario,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> None
        """
        Builds the HTML content for scenario steps.

        :param html: HTML output page to feed.
        :param scenario: Scenario which steps to build HTML content for.
        """
        with html.addcontent('<div id="steps"></div>'):
            html.addcontent('<p>Steps:</p>')
            with html.addcontent('<ul></ul>'):
                for _step in scenario.steps:  # type: _StepDefinitionType
                    self._step(html, _step)

    def _step(
            self,
            html,  # type: _HtmlDocumentType
            step,  # type: _StepDefinitionType
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given step.

        :param html: HTML output page to feed.
        :param step: Step to build HTML content for.
        """
        from .._stepsection import StepSectionDescription

        with html.addcontent('<li class="step"></li>'):
            if isinstance(step, StepSectionDescription) and step.description:
                html.addcontent(f'<h2 class="step">{html.encode(step.description)}</h2>')
            else:
                html.addcontent(f'<span class="step number">step#{step.number}</span>')
                if step.description:
                    html.addcontent('<span class="step sep">:</span>')
                    html.addcontent(f'<span class="step description">{step.description}</span>')
                html.addcontent(f'<span class="step name">({step.name})</span>')

                _req_refs = step.getreqrefs()  # type: _SetWithReqLinksType[_ReqRefType]
                if _req_refs:
                    self._reqrefs(html, step, _req_refs)

                with html.addcontent(f'<div class="actions-results"></div>'):
                    with html.addcontent('<ul></ul>'):
                        for _action_result in step.actions_results:  # type: _ActionResultDefinitionType
                            self._actionresult(html, _action_result)

    def _actionresult(
            self,
            html,  # type: _HtmlDocumentType
            action_result,  # type: _ActionResultDefinitionType
    ):  # type: (...) -> None
        """
        Builds the HTML content for the given action / expected result.

        :param html: HTML output page to feed.
        :param action_result: Action / expected result to build HTML content for.
        """
        with html.addcontent(f'<li class="{action_result.type.lower()}"></li>'):
            html.addcontent(f'<span class="{action_result.type.lower()} type">{action_result.type.upper()}</span>')
            html.addcontent(f'<span class="{action_result.type.lower()} sep">:</span>')
            html.addcontent(f'<span class="{action_result.type.lower()} text">{html.encode(action_result.description)}</span>')

    def _reqrefs(
            self,
            html,  # type: _HtmlDocumentType
            req_verifier,  # type: typing.Union[_ScenarioDefinitionType, _StepDefinitionType]
            req_refs,  # type: _SetWithReqLinksType[_ReqRefType]
    ):  # type: (...) -> None
        """
        Buils the HTML content for a scenario or step requirement coverage.

        :param html: HTML output page to feed.
        :param req_verifier: Scenario or step to process requirement coverage for.
        :param req_refs: Scenario or step requirement coverage.
        """
        from .._reqlink import ReqLink
        from .._scenariodefinition import ScenarioDefinition
        from .._stepdefinition import StepDefinition

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
                        html.addcontent(f'<span class="{_obj_class} req-ref id">{html.encode(_req_ref.id)}</span>')

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
