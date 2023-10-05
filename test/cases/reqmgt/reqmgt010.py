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

import typing

import scenario.test

if True:
    from reqmgt.steps.reqitems import CheckReqItemStep as _CheckReqItemStepImpl  # `CheckReqItemStep` used for inheritance.


class ReqMgt010(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from reqscenario1 import ReqScenario1
        from reqscenario2 import ReqScenario2

        scenario.test.TestCase.__init__(
            self,
            title="Requirement database and queries",
            description="Check the requirement database can be fed from tests being loaded, and queried.",
        )
        self.verifies(
            scenario.test.reqs.REQUIREMENT_MANAGEMENT,
        )

        self.addstep(SaveScenarioTestReqs())
        self.addstep(CreateScenario(ReqScenario1))
        self.addstep(CreateScenario(ReqScenario2))
        self.addstep(CheckReqDbContent())
        self.addstep(CheckUpstreamReqLinks())
        self.addstep(CheckDownstreamReqLinks())

    class Data:
        @property
        def req001(self):  # type: () -> scenario.Req
            return scenario.reqs.getreq("REQ-001")

        @property
        def req001_main(self):  # type: () -> scenario.ReqRef
            return scenario.reqs.getreqref("REQ-001")

        @property
        def req001_1(self):  # type: () -> scenario.ReqRef
            return scenario.reqs.getreqref("REQ-001/1")

        @property
        def req002(self):  # type: () -> scenario.Req
            return scenario.reqs.getreq("REQ-002")

        @property
        def req002_main(self):  # type: () -> scenario.ReqRef
            return scenario.reqs.getreqref("REQ-002")

        @property
        def scenario1(self):  # type: () -> scenario.Scenario
            return CreateScenario.getinstance(0).scenario_instance

        @property
        def scenario2(self):  # type: () -> scenario.Scenario
            return CreateScenario.getinstance(1).scenario_instance

        @property
        def scenario2_step1(self):  # type: () -> scenario.Step
            return CreateScenario.getinstance(1).scenario_instance.steps[0]


class SaveScenarioTestReqs(scenario.Step):

    def __init__(self):  # type: (...) -> None
        scenario.Step.__init__(self)

        self.scenario_reqs = []  # type: scenario.types.OrderedSet[scenario.Req]
        self.scenario_req_refs = []  # type: scenario.types.OrderedSet[scenario.ReqRef]
        self.scenario_req_links = []  # type: scenario.types.OrderedSet[scenario.ReqLink]

    def step(self):  # type: (...) -> None
        self.STEP("`scenario.test` requirements backup")

        if self.ACTION("Save the `scenario.test` requirements, requirement references and links already stored in the requirement database."):
            self.scenario_reqs = scenario.reqs.getallreqs()
            self.scenario_req_refs = scenario.reqs.getallrefs()
            self.scenario_req_links = scenario.reqs.getalllinks()


class CreateScenario(scenario.Step):

    def __init__(
            self,
            scenario_cls,  # type: typing.Type[scenario.Scenario]
    ):  # type: (...) -> None
        scenario.Step.__init__(self)

        self.scenario_cls = scenario_cls  # type: typing.Type[scenario.Scenario]
        self.scenario_instance = scenario.Scenario()  # type: scenario.Scenario

    def step(self):  # type: (...) -> None
        from scenario._reflection import qualname  # noqa  ## Access to protected member

        self.STEP("Scenario creation")

        if self.ACTION(f"Create a {qualname(self.scenario_cls)} instance."):
            self.scenario_instance = self.scenario_cls()


class CheckReqDbContent(_CheckReqItemStepImpl, ReqMgt010.Data):

    def __init__(self):  # type: (...) -> None
        _CheckReqItemStepImpl.__init__(self)

        self.new_reqs = []  # type: scenario.types.OrderedSet[scenario.Req]
        self.new_req_refs = []  # type: scenario.types.OrderedSet[scenario.ReqRef]
        self.new_req_links = []  # type: scenario.types.OrderedSet[scenario.ReqLink]

    def step(self):  # type: (...) -> None
        self.STEP("Requirement database content")

        self._checkreqs()
        self._checkreqrefs()
        self._checkreqlinks()

    def _checkreqs(self):  # type: (...) -> None

        with self.SECTION("Check requirements:"):
            if self.ACTION("Search for new requirements in the requirement database."):
                self.new_reqs = list(filter(
                    lambda req: req not in SaveScenarioTestReqs.getinstance().scenario_reqs,
                    scenario.reqs.getallreqs(),
                ))
            if self.RESULT("Two requirements have been saved in the database:"):
                self.assertlen(self.new_reqs, 2, evidence=True)
            if self.RESULT("1. REQ-001"):
                self.assertequal(self.new_reqs[0].id, "REQ-001", evidence="Requirement id")
            if self.RESULT("2. REQ-002"):
                self.assertequal(self.new_reqs[1].id, "REQ-002", evidence="Requirement id")

    def _checkreqrefs(self):  # type: (...) -> None

        with self.SECTION("Check requirement references:"):
            if self.ACTION("Search for new requirement references in the requirement database."):
                self.new_req_refs = list(filter(
                    lambda req_ref: req_ref not in SaveScenarioTestReqs.getinstance().scenario_req_refs,
                    scenario.reqs.getallrefs(),
                ))
            if self.RESULT("Three requirement references have been saved in the database:"):
                self.assertlen(self.new_req_refs, 3, evidence=True)
            if self.RESULT("1. REQ-001"):
                self.assertequal(self.new_req_refs[0].id, "REQ-001", evidence="Requirement reference id")
            if self.RESULT("2. REQ-001/1"):
                self.assertequal(self.new_req_refs[1].id, "REQ-001/1", evidence="Requirement reference id")
            if self.RESULT("3. REQ-002"):
                self.assertequal(self.new_req_refs[2].id, "REQ-002", evidence="Requirement reference id")

    def _checkreqlinks(self):  # type: (...) -> None

        with self.SECTION("Check requirement links:"):
            if self.ACTION("Search for new requirement links in the requirement database."):
                self.new_req_links = list(filter(
                    lambda req_link: req_link not in SaveScenarioTestReqs.getinstance().scenario_req_links,
                    scenario.reqs.getalllinks(),
                ))
            if self.RESULT("Four requirement links have been saved in the database:"):
                self.assertlen(self.new_req_links, 4, evidence=True)
                for _req_link in self.new_req_links:  # type: scenario.ReqLink
                    self.debug(f"{_req_link!r}")
            if self.RESULT("1. between REQ-001 and the ReqScenario1 scenario, "
                           "without comments,"):
                self.checkreqlink(
                    self.new_req_links[0],
                    req_ref=("REQ-001", ()), req_verifiers=[self.scenario1],
                    comments="",
                    evidence=True,
                )
            if self.RESULT("2. between REQ-001/1 and ReqScenario2, "
                           "with 'Justification for REQ-001/1 covered by ReqScenario2' for comments,"):
                self.checkreqlink(
                    self.new_req_links[1],
                    req_ref=("REQ-001", ("1", )), req_verifiers=[self.scenario2],
                    comments="Justification for REQ-001/1 covered by ReqScenario2",
                    evidence=True,
                )
            if self.RESULT("3. between REQ-001/1 and ReqScenario2/step#1, "
                           "with 'Justification for REQ-001/1 covered by ReqScenario2:step#1' for comments,"):
                self.checkreqlink(
                    self.new_req_links[2],
                    req_ref=("REQ-001", ("1", )), req_verifiers=[self.scenario2_step1],
                    comments="Justification for REQ-001/1 covered by ReqScenario2:step#1",
                    evidence=True,
                )
            if self.RESULT("4. between REQ-002 and the ReqScenario2 scenario, "
                           "without comments."):
                self.checkreqlink(
                    self.new_req_links[3],
                    req_ref=("REQ-002", ()), req_verifiers=[self.scenario2],
                    comments="",
                    evidence=True,
                )


class CheckUpstreamReqLinks(_CheckReqItemStepImpl, ReqMgt010.Data):

    def step(self):  # type: (...) -> None
        self.STEP("Upstream requirement links")

        self._checkreqlinks()
        self._checkreqrefs()
        self._checkreqs()

    def _checkreqlinks(self):  # type: (...) -> None

        with self.SECTION("Check requirement links:"):
            _direct_req_links = []  # type: scenario.types.OrderedSet[scenario.ReqLink]
            if self.ACTION("Retrieve ReqScenario1 direct requirement links."):
                _direct_req_links = self.scenario1.getreqlinks(walk_steps=False)
            if self.RESULT("The scenario owns 1 link, from the scenario:"):
                self.assertlen(_direct_req_links, 1, evidence=True)
            if self.RESULT("1. to the main part of REQ-001."):
                self.checkreqlink(_direct_req_links[0], self.req001_main, [self.scenario1], evidence=True)

            _all_req_links = []  # type: scenario.types.OrderedSet[scenario.ReqLink]
            if self.ACTION("Retrieve all ReqScenario1 requirement links (including step links)."):
                _all_req_links = self.scenario1.getreqlinks(walk_steps=True)
            if self.RESULT("Same result."):
                self.assertequal(_all_req_links, _direct_req_links, evidence=True)

            if self.ACTION("Retrieve ReqScenario2 direct requirement links."):
                _direct_req_links = self.scenario2.getreqlinks(walk_steps=False)
            if self.RESULT("The scenario owns 2 links:"):
                self.assertlen(_direct_req_links, 2, evidence=True)
            if self.RESULT("1. to the REQ-001/1 sub-part of REQ-001,"):
                self.checkreqlink(_direct_req_links[0], self.req001_1, [self.scenario2], evidence=True)
            if self.RESULT("2. to the main part of REQ-002."):
                self.checkreqlink(_direct_req_links[1], self.req002_main, [self.scenario2], evidence=True)

            if self.ACTION("Retrieve all ReqScenario2 requirement links (including step links)."):
                _all_req_links = self.scenario2.getreqlinks(walk_steps=True)
            if self.RESULT("The result contains 1 more link:"):
                self.assertlen(_all_req_links, 3, evidence=True)
                self.assertsameinstances(_all_req_links[0], _direct_req_links[0], evidence=False)
                self.assertsameinstances(_all_req_links[2], _direct_req_links[1], evidence=False)
            if self.RESULT("- to the REQ-001/1 sub-part of REQ-001, from ReqScenario2/step#1."):
                self.checkreqlink(_all_req_links[1], self.req001_1, [self.scenario2_step1], evidence=True)

            if self.ACTION("Retrieve ReqScenario2/step#1 requirement links."):
                _direct_req_links = self.scenario2_step1.getreqlinks()
            if self.RESULT("The step owns 1 link:"):
                self.assertlen(_direct_req_links, 1, evidence=True)
            if self.RESULT("1. to the REQ-001/1 sub-part of REQ-001."):
                self.checkreqlink(_direct_req_links[0], self.req001_1, [self.scenario2_step1], evidence=True)

    def _checkreqrefs(self):  # type: (...) -> None

        with self.SECTION("Check requirement references:"):
            _direct_req_refs = {}  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
            if self.ACTION("Retrieve direct requirement references from ReqScenario1."):
                _direct_req_refs = self.scenario1.getreqrefs(walk_steps=False)
            if self.RESULT("The scenario traces 1 requirement reference:"):
                self.assertlen(_direct_req_refs, 1, evidence=True)
            if self.RESULT("1. REQ-001 (main part)"):
                self.checkiteminsetwithreqlinks(
                    self.req001_main, _direct_req_refs, [(self.req001_main, [self.scenario1])],
                    evidence=True,
                )

            _all_req_refs = {}  # type: scenario.SetWithReqLinksType[scenario.ReqRef]
            if self.ACTION("Retrieve all requirement references from ReqScenario1 (including step references)."):
                _all_req_refs = self.scenario1.getreqrefs(walk_steps=True)
            if self.RESULT("Same result."):
                self.assertequal(_all_req_refs, _direct_req_refs, evidence=True)

            if self.ACTION("Retrieve direct requirement references from ReqScenario2."):
                _direct_req_refs = self.scenario2.getreqrefs(walk_steps=False)
            if self.RESULT("The scenario traces 2 requirement references:"):
                self.assertlen(_direct_req_refs, 2, evidence=True)
            if self.RESULT("1. REQ-001/1 (sub-part),"):
                self.checkiteminsetwithreqlinks(
                    self.req001_1, _direct_req_refs, [(self.req001_1, [self.scenario2])],
                    evidence=True,
                )
            if self.RESULT("2. REQ-002 (main part)."):
                self.checkiteminsetwithreqlinks(
                    self.req002_main, _direct_req_refs, [(self.req002_main, [self.scenario2])],
                    evidence=True,
                )

            if self.ACTION("Retrieve all requirement references from ReqScenario2 (including step references)."):
                _all_req_refs = self.scenario2.getreqrefs(walk_steps=True)
            if self.RESULT("The scenario still traces 2 requirement references:"):
                self.assertlen(_all_req_refs, 2, evidence=True)
            if self.RESULT("1. REQ-001/1 (sub-part), with 1 more link from ReqScenario2/step#1,"):
                self.checkiteminsetwithreqlinks(
                    self.req001_1, _all_req_refs, [(self.req001_1, [self.scenario2]), (self.req001_1, [self.scenario2_step1])],
                    evidence=True,
                )
            if self.RESULT("2. REQ-002 (main part), with the same single link from ReqScenario2."):
                self.checkiteminsetwithreqlinks(
                    self.req002_main, _all_req_refs, [(self.req002_main, [self.scenario2])],
                    evidence=True,
                )

            if self.ACTION("Retrieve ReqScenario2/step#1 requirement references."):
                _direct_req_refs = self.scenario2_step1.getreqrefs()
            if self.RESULT("The step traces 1 requirement reference:"):
                self.assertlen(_direct_req_refs, 1, evidence=True)
            if self.RESULT("1. REQ-001/1 (sub-part)."):
                self.checkiteminsetwithreqlinks(
                    self.req001_1, _direct_req_refs, [(self.req001_1, [self.scenario2_step1])],
                    evidence=True,
                )

    def _checkreqs(self):  # type: (...) -> None

        with self.SECTION("Check requirements:"):
            _direct_reqs = {}  # type: scenario.types.SetWithReqLinks[scenario.Req]
            if self.ACTION("Retrieve direct requirements from ReqScenario1."):
                _direct_reqs = self.scenario1.getreqs(walk_steps=False)
            if self.RESULT("The scenario traces 1 requirement:"):
                self.assertlen(_direct_reqs, 1, evidence=True)
            if self.RESULT("1. REQ-001."):
                self.checkiteminsetwithreqlinks(
                    self.req001, _direct_reqs, [(self.req001_main, [self.scenario1])],
                    evidence=True,
                )

            _all_reqs = {}  # type: scenario.types.SetWithReqLinks[scenario.Req]
            if self.ACTION("Retrieve all requirements from ReqScenario1."):
                _all_reqs = self.scenario1.getreqs(walk_steps=True)
            if self.RESULT("Same result."):
                self.assertequal(_all_reqs, _direct_reqs, evidence=True)

            if self.ACTION("Retrieve direct requirements from ReqScenario2."):
                _direct_reqs = self.scenario2.getreqs(walk_steps=False)
            if self.RESULT("The scenario traces 2 requirements:"):
                self.assertlen(_direct_reqs, 2, evidence=True)
            if self.RESULT("1. REQ-001,"):
                self.checkiteminsetwithreqlinks(
                    self.req001, _direct_reqs, [(self.req001_1, [self.scenario2])],
                    evidence=True,
                )
            if self.RESULT("2. REQ-002."):
                self.checkiteminsetwithreqlinks(
                    self.req002, _direct_reqs, [(self.req002_main, [self.scenario2])],
                    evidence=True,
                )

            if self.ACTION("Retrieve all requirements from ReqScenario2."):
                _all_reqs = self.scenario2.getreqs(walk_steps=True)
            if self.RESULT("The scenario still traces 2 requirements:"):
                self.assertlen(_all_reqs, 2, evidence=True)
            if self.RESULT("1. REQ-001, through its REQ-001/1 sub-part, with 1 more link from ReqScenario2/step#1,"):
                self.checkiteminsetwithreqlinks(
                    self.req001, _all_reqs, [(self.req001_1, [self.scenario2]), (self.req001_1, [self.scenario2_step1])],
                    evidence=True,
                )
            if self.RESULT("2. REQ-002, with the same single link from ReqScenario2."):
                self.checkiteminsetwithreqlinks(
                    self.req002, _all_reqs, [(self.req002_main, [self.scenario2])],
                    evidence=True,
                )

            if self.ACTION("Retrieve ReqScenario2/step#1 requirements."):
                _direct_reqs = self.scenario2_step1.getreqs()
            if self.RESULT("The step traces 1 requirement:"):
                self.assertlen(_direct_reqs, 1, evidence=True)
            if self.RESULT("1. REQ-001."):
                self.checkiteminsetwithreqlinks(
                    self.req001, _direct_reqs, [(self.req001_1, [self.scenario2_step1])],
                    evidence=True,
                )


class CheckDownstreamReqLinks(_CheckReqItemStepImpl, ReqMgt010.Data):

    def step(self):  # type: (...) -> None
        self.STEP("Downstream requirement links")

        self._checkreqlinks()
        self._checkreqverifiers()
        self._checkscenarios()

    def _checkreqlinks(self):  # type: (...) -> None
        with self.SECTION("Check requirement links:"):
            _direct_req_links = []  # type: typing.Sequence[scenario.ReqLink]
            if self.ACTION("Retrieve REQ-001 direct requirement links."):
                _direct_req_links = self.req001.getreqlinks(walk_sub_refs=False)
            if self.RESULT("The requirement is traced by 1 link directly:"):
                self.assertlen(_direct_req_links, 1, evidence=True)
            if self.RESULT("1. from ReqScenario1."):
                self.checkreqlink(_direct_req_links[0], self.req001_main, [self.scenario1], evidence=True)

            _all_req_links = []  # type: typing.Sequence[scenario.ReqLink]
            if self.ACTION("Retrieve all REQ-001 requirement links (including sub-ref links)."):
                _all_req_links = self.req001.getreqlinks(walk_sub_refs=True)
            if self.RESULT("The result contains 2 more links:"):
                self.assertlen(_all_req_links, 3, evidence=True)
                self.assertsameinstances(_all_req_links[0], _direct_req_links[0], evidence=False)
            if self.RESULT("1. from ReqScenario2, to the REQ-001/1 sub-part,"):
                self.checkreqlink(_all_req_links[1], self.req001_1, [self.scenario2], evidence=True)
            if self.RESULT("2. from ReqScenario2/step#1, to the REQ-001/1 sub-part."):
                self.checkreqlink(_all_req_links[2], self.req001_1, [self.scenario2_step1], evidence=True)

            if self.ACTION("Retrieve REQ-001/1 requirement links."):
                _direct_req_links = self.req001_1.getreqlinks()
            if self.RESULT("The result contains 2 links:"):
                self.assertlen(_direct_req_links, 2, evidence=True)
            if self.RESULT("1. from ReqScenario2,"):
                self.checkreqlink(_direct_req_links[0], self.req001_1, [self.scenario2], evidence=True)
            if self.RESULT("2. from ReqScenario2/step#1."):
                self.checkreqlink(_direct_req_links[1], self.req001_1, [self.scenario2_step1], evidence=True)

            if self.ACTION("Retrieve REQ-002 direct requirement links."):
                _direct_req_links = self.req002.getreqlinks(walk_sub_refs=False)
            if self.RESULT("The requirement is traced by 1 link directly:"):
                self.assertlen(_direct_req_links, 1, evidence=True)
            if self.RESULT("1. from ReqScenario2, to the main part of REQ-002."):
                self.checkreqlink(_direct_req_links[0], self.req002_main, [self.scenario2], evidence=True)

            if self.ACTION("Retrieve all REQ-002 requirement links (including sub-ref links)."):
                _all_req_links = self.req002.getreqlinks(walk_sub_refs=True)
            if self.RESULT("Same result."):
                self.assertequal(_all_req_links, _direct_req_links, evidence=True)

    def _checkreqverifiers(self):  # type: (...) -> None
        with self.SECTION("Check requirement verifiers:"):
            _direct_req_verifiers = {}  # type: scenario.SetWithReqLinksType[scenario.ReqVerifier]
            if self.ACTION("Retrieve REQ-001 direct requirement verifiers."):
                _direct_req_verifiers = self.req001.getverifiers(walk_sub_refs=False)
            if self.RESULT("The requirement is traced by 1 verifier directly:"):
                self.assertlen(_direct_req_verifiers, 1, evidence=True)
            if self.RESULT("1. ReqScenario1."):
                self.checkiteminsetwithreqlinks(
                    self.scenario1, _direct_req_verifiers, [(self.req001_main, [self.scenario1])],
                    evidence=True,
                )

            _all_req_verifiers = {}  # type: scenario.SetWithReqLinksType[scenario.ReqVerifier]
            if self.ACTION("Retrieve all REQ-001 requirement verifiers (including sub-ref verifiers)."):
                _all_req_verifiers = self.req001.getverifiers(walk_sub_refs=True)
            if self.RESULT("The result contains 3 requirement verifiers:"):
                self.assertlen(_all_req_verifiers, 3, evidence=True)
            if self.RESULT("1. ReqScenario1, tracing REQ-001 (main-part)."):
                self.checkiteminsetwithreqlinks(
                    self.scenario1, _all_req_verifiers, [(self.req001_main, [self.scenario1])],
                    evidence=True,
                )
            if self.RESULT("2. ReqScenario2, tracing REQ-001/1,"):
                self.checkiteminsetwithreqlinks(
                    self.scenario2, _all_req_verifiers, [(self.req001_1, [self.scenario2])],
                    evidence=True,
                )
            if self.RESULT("3. ReqScenario2/step#1, tracing REQ-001/1."):
                self.checkiteminsetwithreqlinks(
                    self.scenario2_step1, _all_req_verifiers, [(self.req001_1, [self.scenario2_step1])],
                    evidence=True,
                )

            if self.ACTION("Retrieve REQ-001/1 requirement verifiers."):
                _direct_req_verifiers = self.req001_1.getverifiers()
            if self.RESULT("The requirement sub-part is traced by 2 verifiers:"):
                self.assertlen(_direct_req_verifiers, 2, evidence=True)
            if self.RESULT("1. ReqScenario2,"):
                self.checkiteminsetwithreqlinks(
                    self.scenario2, _direct_req_verifiers, [(self.req001_1, [self.scenario2])],
                    evidence=True,
                )
            if self.RESULT("2. ReqScenario2/step#1."):
                self.checkiteminsetwithreqlinks(
                    self.scenario2_step1, _direct_req_verifiers, [(self.req001_1, [self.scenario2_step1])],
                    evidence=True,
                )

            if self.ACTION("Retrieve REQ-002 direct requirement verifiers."):
                _direct_req_verifiers = self.req002.getverifiers(walk_sub_refs=False)
            if self.RESULT("The requirement is traced by 1 verifier directly:"):
                self.assertlen(_direct_req_verifiers, 1, evidence=True)
            if self.RESULT("1. ReqScenario2."):
                self.checkiteminsetwithreqlinks(
                    self.scenario2, _direct_req_verifiers, [(self.req002_main, [self.scenario2])],
                    evidence=True,
                )

            if self.ACTION("Retrieve all REQ-002 requirement verifiers (including sub-ref verifiers)."):
                _all_req_verifiers = self.req002.getverifiers(walk_sub_refs=True)
            if self.RESULT("Same result."):
                self.assertequal(_all_req_verifiers, _direct_req_verifiers, evidence=True)

    def _checkscenarios(self):  # type: (...) -> None
        with self.SECTION("Check requirement verifiers:"):
            _direct_scenarios = {}  # type: scenario.SetWithReqLinksType[scenario.ScenarioDefinition]
            if self.ACTION("Retrieve REQ-001 direct scenarios."):
                _direct_scenarios = self.req001.getscenarios(walk_sub_refs=False)
            if self.RESULT("The requirement is traced by 1 scenario directly:"):
                self.assertlen(_direct_scenarios, 1, evidence=True)
            if self.RESULT("1. ReqScenario1."):
                self.checkiteminsetwithreqlinks(
                    self.scenario1, _direct_scenarios, [(self.req001_main, [self.scenario1])],
                    evidence=True,
                )

            _all_scenarios = {}  # type: scenario.SetWithReqLinksType[scenario.ScenarioDefinition]
            if self.ACTION("Retrieve all REQ-001 scenarios (including sub-ref scenarios)."):
                _all_scenarios = self.req001.getscenarios(walk_sub_refs=True)
            if self.RESULT("The result contains 2 scenarios:"):
                self.assertlen(_all_scenarios, 2, evidence=True)
            if self.RESULT("1. ReqScenario1, still tracing REQ-001 (main part),"):
                self.checkiteminsetwithreqlinks(
                    self.scenario1, _all_scenarios, [(self.req001_main, [self.scenario1])],
                    evidence=True,
                )
            if self.RESULT("2. ReqScenario2, tracing REQ-001/1 twice from ReqScenario2 and ReqScenario2/step#1."):
                self.checkiteminsetwithreqlinks(
                    self.scenario2, _all_scenarios, [(self.req001_1, [self.scenario2]), (self.req001_1, [self.scenario2_step1])],
                    evidence=True,
                )

            if self.ACTION("Retrieve REQ-001/1 scenarios."):
                _direct_scenarios = self.req001_1.getscenarios()
            if self.RESULT("The requirement sub-part is traced by 1 scenario:"):
                self.assertlen(_direct_scenarios, 1, evidence=True)
            if self.RESULT("1. ReqScenario2, tracing it twice from ReqScenario2 and ReqScenario2/step#1."):
                self.checkiteminsetwithreqlinks(
                    self.scenario2, _direct_scenarios, [(self.req001_1, [self.scenario2]), (self.req001_1, [self.scenario2_step1])],
                    evidence=True,
                )

            if self.ACTION("Retrieve REQ-002 direct scenarios."):
                _direct_scenarios = self.req002.getscenarios(walk_sub_refs=False)
            if self.RESULT("The requirement is traced by 1 scenario directly:"):
                self.assertlen(_direct_scenarios, 1, evidence=True)
            if self.RESULT("1. ReqScenario2."):
                self.checkiteminsetwithreqlinks(
                    self.scenario2, _direct_scenarios, [(self.req002_main, [self.scenario2])],
                    evidence=True,
                )

            if self.ACTION("Retrieve all REQ-002 scenarios (including sub-ref scenarios)."):
                _all_scenarios = self.req002.getscenarios(walk_sub_refs=True)
            if self.RESULT("Same result."):
                self.assertequal(_all_scenarios, _direct_scenarios, evidence=True)
