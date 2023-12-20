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
        assert self.campaign_expectations.req_db_file.content_path is not None, "Requirement content file missing in campaign expectations"
        _expected_req_db = JsonDict.readfile(self.campaign_expectations.req_db_file.content_path)  # type: scenario.types.JsonDict

        # Ensure the `CampaignExpectations` object knows the campaign output directory path.
        if self.doexecute():
            self.campaign_expectations.outdir_path = self.getexecstep(ExecCampaign).final_outdir_path

        _req_db = {}  # type: scenario.types.JsonDict
        if self.ACTION("Read the requirement file."):
            self.evidence(f"Requirement file: {self.campaign_expectations.req_db_file.path}")
            _req_db = JsonDict.readfile(self.campaign_expectations.req_db_file.path)

        def _reqids(req_db_json):  # type: (scenario.types.JsonDict) -> typing.List[str]
            return list(
                filter(
                    lambda key: key not in ["$encoding", "$license", "$schema", "$version"],
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
                if self.campaign_expectations.req_db_file.with_titles_and_texts is True:
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
                elif self.campaign_expectations.req_db_file.with_titles_and_texts is False:
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
                _subrefs_txt = scenario.text.Countable("subreference", _expected_req["subrefs"])  # type: scenario.text.Countable
                if self.RESULT(f"with {len(_subrefs_txt)} {_subrefs_txt}{_subrefs_txt.ifany(':', '.')}"):
                    self.assertin("subrefs", _req, evidence=False)
                    self.assertlen(
                        _req["subrefs"], len(_expected_req["subrefs"]),
                        evidence=True,
                    )
                for _index, _expected_subref_id in enumerate(_expected_req["subrefs"]):  # type: int, str
                    if self.RESULT(f"- {_expected_subref_id}"):
                        self.assertequal(
                            _req["subrefs"][_index], _expected_subref_id,
                            evidence=True,
                        )
