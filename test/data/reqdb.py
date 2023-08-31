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

import scenario


REQ_001 = scenario.Req(
    id="REQ-001",
    title="Ping / Main path",
    text="\n".join([
        "1. SUT receives a PING message.",
        "2. SUT responds a PONG message.",
    ]),
)  # type: scenario.Req

REQ_002 = scenario.Req(
    id="REQ-002",
    title="Ping / Querier black list",
    text="\n".join([
        "Alternate of REQ-001/1.",
        "",
        "If the querier is part of the black list,",
        "then SUT responds nothing.",
    ])
)  # type: scenario.Req


def loadreqdb():  # type: (...) -> None
    scenario.reqs.push(REQ_001)
    scenario.reqs.push(REQ_002)
