#!/usr/bin/env python
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

import pathlib
import sys
import typing

# Path management.
_root_scenario_path = pathlib.Path(__file__).parents[1].resolve()  # type: pathlib.Path
sys.path.append(str(_root_scenario_path / "src"))
sys.path.append(str(_root_scenario_path / "test" / "cases"))
sys.path.append(str(_root_scenario_path / "test" / "src"))

if True:
    import scenario  # @after-path-management
    import scenario.reqs  # @after-path-management
    import scenario.test  # @after-path-management


# Command line arguments.
class ScenarioReqManagementArgs(scenario.ReqManagementArgs):

    def __init__(self):  # type: (...) -> None
        scenario.ReqManagementArgs.__init__(self)
        self.setdescription("Scenario tests requirement management.")

    def _checkargs(
            self,
            args,  # type: typing.Any
    ):  # type: (...) -> bool
        # In case of default requirements and default test suites, consider default outputs.
        if (not self.req_db_paths) and (not self.test_suite_paths):
            if (not self.downstream_traceability_outfile) and (not self.upstream_traceability_outfile):
                self.debug("Using default paths for upstream an downstream traceability outputs: '%s' and '%s'",
                           scenario.reqs.paths.DOWNSTREAM_TRACEABILITY, scenario.reqs.paths.UPSTREAM_TRACEABILITY)
                self.downstream_traceability_outfile = scenario.reqs.paths.DOWNSTREAM_TRACEABILITY
                self.upstream_traceability_outfile = scenario.reqs.paths.UPSTREAM_TRACEABILITY

        if not super()._checkargs(args):
            return False

        return True


if __name__ == "__main__":
    # Parse arguments.
    scenario.ReqManagementArgs.setinstance(ScenarioReqManagementArgs())
    if not ScenarioReqManagementArgs.getinstance().parse(sys.argv[1:]):
        sys.exit(int(ScenarioReqManagementArgs.getinstance().error_code))

    # Set main path after arguments have been parsed.
    scenario.Path.setmainpath(scenario.test.paths.ROOT_SCENARIO_PATH)

    # Ensure defaults:
    # - requirements,
    if not ScenarioReqManagementArgs.getinstance().req_db_paths:
        scenario.reqs.load(set_default_req_file=True)
    # - test suites,
    if not ScenarioReqManagementArgs.getinstance().test_suite_paths:
        scenario.reqs.setdefaulttestsuites()
    # - default outputs already ensured in `ScenarioReqManagementArgs._checkargs()`.

    # Requirement management execution.
    _res = scenario.req_mgt.main()  # type: scenario.ErrorCode

    # Add license headers to default traceability files if updated.
    try:
        if ScenarioReqManagementArgs.getinstance().downstream_traceability_outfile == scenario.reqs.paths.DOWNSTREAM_TRACEABILITY:
            scenario.reqs.ensurelicenseheader(scenario.reqs.paths.DOWNSTREAM_TRACEABILITY)
        if ScenarioReqManagementArgs.getinstance().upstream_traceability_outfile == scenario.reqs.paths.UPSTREAM_TRACEABILITY:
            scenario.reqs.ensurelicenseheader(scenario.reqs.paths.UPSTREAM_TRACEABILITY)
    except Exception as _err:
        scenario.logging.logexceptiontraceback(_err)
        _res = scenario.ErrorCode.worst([_res, scenario.ErrorCode.fromexception(_err)])

    sys.exit(int(_res))
