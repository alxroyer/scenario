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

import scenario
import scenario.test
import scenario.text

if typing.TYPE_CHECKING:
    from campaigns.steps.execution import ExecCampaign as _ExecCampaignType


class CheckCampaignReqDbFile(scenario.test.VerificationStep):

    def __init__(
            self,
            exec_step,  # type: _ExecCampaignType
            campaign_expectations,  # type: scenario.test.CampaignExpectations
    ):  # type: (...) -> None
        scenario.test.VerificationStep.__init__(self, exec_step)

        self.campaign_expectations = campaign_expectations  # type: scenario.test.CampaignExpectations

    def step(self):  # type: (...) -> None
        from scenario._jsondictutils import JsonDict  # noqa  ## Access to protected module
        from campaigns.steps.execution import ExecCampaign

        self.STEP("Requirement database file content")

        # Expected requirements.
        assert isinstance(self.campaign_expectations.req_db_file, scenario.Path), "Requirement file missing in campaign expectations"
        _expected_req_db = JsonDict.readfile(self.campaign_expectations.req_db_file)  # type: scenario.types.JsonDict

        _req_db = {}  # type: scenario.types.JsonDict
        if self.ACTION("Read the requirement file."):
            self.evidence(f"Requirement file: {self.getexecstep(ExecCampaign).req_db_path}")
            _req_db = JsonDict.readfile(self.getexecstep(ExecCampaign).req_db_path)

        def _reqids(req_db_json):  # type: (scenario.types.JsonDict) -> typing.List[str]
            return list(
                filter(
                    lambda key: key not in ["$license", "$schema", "$version"],
                    req_db_json.keys(),
                ),
            )

        _reqs_txt = scenario.text.Countable("requirement", _reqids(_expected_req_db))  # type: scenario.text.Countable
        if self.RESULT(f"The requirement file contains {len(_reqs_txt)} {_reqs_txt}{_reqs_txt.ifany(':', '.')}"):
            self.assertlen(
                _reqids(_req_db), len(_reqids(_expected_req_db)),
                evidence=True,
            )

        for _req_id in _reqids(_expected_req_db):  # type: str
            _expected_req = _expected_req_db[_req_id]  # type: scenario.types.JsonDict
            _req = {}  # type: scenario.types.JsonDict
            if self.RESULT(f"- {_req_id}"):
                self.assertin(
                    _req_id, _req_db,
                    evidence=True,
                )
                _req = _req_db[_req_id]
                del _req_db[_req_id]
            with scenario.logging.pushindentation("  "):
                if self.RESULT(f"with id: {_expected_req['id']}"):
                    self.assertin("id", _req, evidence=False)
                    self.assertequal(
                        _req["id"], _expected_req["id"],
                        evidence=True,
                    )
                if self.campaign_expectations.req_db_file_titles_and_texts is True:
                    if self.RESULT(f"with title: {_expected_req['title']}"):
                        self.assertin("title", _req, evidence=False)
                        self.assertequal(
                            _req["title"], _expected_req["title"],
                            evidence=True,
                        )
                    if self.RESULT(f"with text: {_expected_req['text']}"):
                        self.assertin("text", _req, evidence=False)
                        self.assertequal(
                            _req["text"], _expected_req["text"],
                            evidence=True,
                        )
                elif self.campaign_expectations.req_db_file_titles_and_texts is False:
                    if self.RESULT(f"without title"):
                        if "title" in _req:
                            self.assertisempty(
                                _req["title"],
                                evidence=True,
                            )
                        else:
                            self.assertnotin(
                                "title", _req,
                                evidence=True,
                            )
                    if self.RESULT(f"without text"):
                        if "text" in _req:
                            self.assertisempty(
                                _req["text"],
                                evidence=True,
                            )
                        else:
                            self.assertnotin(
                                "text", _req,
                                evidence=True,
                            )
                _sub_refs_txt = scenario.text.Countable("sub-reference", _expected_req["sub-refs"])  # type: scenario.text.Countable
                if self.RESULT(f"with {len(_sub_refs_txt)} {_sub_refs_txt}{_sub_refs_txt.ifany(':', '.')}"):
                    self.assertin("sub-refs", _req, evidence=False)
                    self.assertlen(
                        _req["sub-refs"], len(_expected_req["sub-refs"]),
                        evidence=True,
                    )
                for _index, _expected_sub_ref_id in enumerate(_expected_req["sub-refs"]):  # type: int, str
                    if self.RESULT(f"- {_expected_sub_ref_id}"):
                        self.assertequal(
                            _req["sub-refs"][_index], _expected_sub_ref_id,
                            evidence=True,
                        )
