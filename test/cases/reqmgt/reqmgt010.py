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


class ReqMgt010(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from reqscenario1 import ReqScenario1
        from reqscenario2 import ReqScenario2

        scenario.test.TestCase.__init__(
            self,
            title="Requirement database and queries",
            description="Check the requirement database can be fed from tests being loaded, and queried.",
        )
        self.covers(
            scenario.test.reqs.REQUIREMENT_MANAGEMENT,
        )

        self.addstep(SaveScenarioTestReqs())
        self._1 = self.addstep(CreateScenario(ReqScenario1))
        self._2 = self.addstep(CreateScenario(ReqScenario2))
        self.addstep(CheckReqDbContent())

    @property
    def scenario1(self):  # type: () -> scenario.Scenario
        return self._1.scenario_instance

    @property
    def scenario2(self):  # type: () -> scenario.Scenario
        return self._2.scenario_instance


class SaveScenarioTestReqs(scenario.Step):

    def __init__(self):  # type: (...) -> None
        scenario.Step.__init__(self)

        self.reqs = []  # type: typing.Sequence[scenario.Req]
        self.req_refs = []  # type: typing.Sequence[scenario.ReqRef]
        self.req_links = []  # type: typing.Sequence[scenario.ReqLink]

    def step(self):  # type: (...) -> None
        self.STEP("`scenario.test` requirements backup")

        if self.ACTION("Save the `scenario.test` requirements, requirement references and links already stored in the requirement database."):
            self.reqs = scenario.reqs.getallreqs()
            self.req_refs = scenario.reqs.getallrefs()
            self.req_links = scenario.reqs.getalllinks()


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


class CheckReqDbContent(scenario.Step):

    def __init__(self):  # type: (...) -> None
        scenario.Step.__init__(self)

        self.reqs = []  # type: typing.Sequence[scenario.Req]
        self.req_refs = []  # type: typing.Sequence[scenario.ReqRef]
        self.req_links = []  # type: typing.Sequence[scenario.ReqLink]

    def step(self):  # type: (...) -> None
        self.STEP("Requirement database content")

        if self.ACTION("Search for new requirements in the requirement database."):
            self.reqs = list(filter(
                lambda req: req not in SaveScenarioTestReqs.getinstance().reqs,
                scenario.reqs.getallreqs(),
            ))
        if self.RESULT("Two requirements have been saved in the database:"):
            self.assertlen(self.reqs, 2, evidence=True)
        if self.RESULT("- REQ-001"):
            self.assertin("REQ-001", [_req.id for _req in self.reqs], evidence=True)
        if self.RESULT("- REQ-002"):
            self.assertin("REQ-002", [_req.id for _req in self.reqs], evidence=True)

        if self.ACTION("Search for new requirement references in the requirement database."):
            self.req_refs = list(filter(
                lambda req_ref: req_ref not in SaveScenarioTestReqs.getinstance().req_refs,
                scenario.reqs.getallrefs(),
            ))
        if self.RESULT("Three requirement references have been saved in the database:"):
            self.assertlen(self.req_refs, 3, evidence=True)
        if self.RESULT("- REQ-001"):
            self.assertin("REQ-001", (_req_ref.id for _req_ref in self.req_refs), evidence=True)
        if self.RESULT("- REQ-001/1"):
            self.assertin("REQ-001/1", [_req_ref.id for _req_ref in self.req_refs], evidence=True)
        if self.RESULT("- REQ-002"):
            self.assertin("REQ-002", [_req_ref.id for _req_ref in self.req_refs], evidence=True)

        if self.ACTION("Search for new requirement links in the requirement database."):
            self.req_links = list(filter(
                lambda req_link: req_link not in SaveScenarioTestReqs.getinstance().req_links,
                scenario.reqs.getalllinks(),
            ))
        if self.RESULT("Four requirement links have been saved in the database:"):
            self.assertlen(self.req_links, 4, evidence=True)
            for _req_link in self.req_links:  # type: scenario.ReqLink
                self.debug(f"{_req_link!r}")
        if self.RESULT("1. between REQ-001 and the ReqScenario1 scenario, without justification,"):
            _req_link = self.req_links[0]  # Type already defined above.
            self.assertequal(_req_link.req_ref.id, "REQ-001", evidence="Requirement reference")
            self.assertlen(_req_link.req_trackers, 1, evidence=False)
            self.assertsameinstances(_req_link.req_trackers[0], ReqMgt010.getinstance().scenario1, evidence="Single tracker")
            self.assertisempty(_req_link.comments, evidence="Comments")
        if self.RESULT("2. between REQ-001 and ReqScenario1's step, with 'Justification for REQ-001 covered by ReqScenario1-step#1' for justification,"):
            _req_link = self.req_links[1]  # Type already defined above.
            self.assertequal(_req_link.req_ref.id, "REQ-001", evidence="Requirement reference")
            self.assertlen(_req_link.req_trackers, 1, evidence=False)
            self.assertsameinstances(_req_link.req_trackers[0], ReqMgt010.getinstance().scenario1.steps[0], evidence="Single tracker")
            self.assertequal(_req_link.comments, "Justification for REQ-001 covered by ReqScenario1-step#1", evidence="Comments")
        if self.RESULT("3. between REQ-001/1 and the ReqScenario2 scenario, without justification,"):
            _req_link = self.req_links[2]  # Type already defined above.
            self.assertequal(_req_link.req_ref.id, "REQ-001/1", evidence="Requirement reference")
            self.assertlen(_req_link.req_trackers, 1, evidence=False)
            self.assertsameinstances(_req_link.req_trackers[0], ReqMgt010.getinstance().scenario2, evidence="Single tracker")
            self.assertisempty(_req_link.comments, evidence="Comments")
        if self.RESULT("4. between REQ-002 and the ReqScenario2 scenario, without justification."):
            _req_link = self.req_links[3]  # Type already defined above.
            self.assertequal(_req_link.req_ref.id, "REQ-002", evidence="Requirement reference")
            self.assertlen(_req_link.req_trackers, 1, evidence=False)
            self.assertsameinstances(_req_link.req_trackers[0], ReqMgt010.getinstance().scenario2, evidence="Single tracker")
            self.assertisempty(_req_link.comments, evidence="Comments")
