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


# Package dependencies.
if True:
    from ._pkgdeps import checkpkgdeps as _checkpkgdeps  # @module-level-execution
    _checkpkgdeps()


# Requirement reexports, in order of definition.
if True:
    from ._reqs import SCENARIO_REQ_BASELINE as _SCENARIO_REQ_BASELINE  # @module-level-instantiation
    req_baseline = _SCENARIO_REQ_BASELINE
    req_db = _SCENARIO_REQ_BASELINE.req_db

    from ._reqs import SCENARIO_EXECUTION as SCENARIO_EXECUTION
    from ._reqs import DOC_ONLY as DOC_ONLY
    from ._reqs import ERROR_HANDLING as ERROR_HANDLING
    from ._reqs import EVIDENCE as EVIDENCE
    from ._reqs import KNOWN_ISSUES as KNOWN_ISSUES
    from ._reqs import LOGGING as LOGGING
    from ._reqs import LOGGING_FILE as LOGGING_FILE
    from ._reqs import DEBUG_LOGGING as DEBUG_LOGGING
    from ._reqs import SCENARIO_LOGGING as SCENARIO_LOGGING
    from ._reqs import SCENARIO_REPORT as SCENARIO_REPORT
    from ._reqs import STATISTICS as STATISTICS
    from ._reqs import ALTERNATIVE_SCENARIOS as ALTERNATIVE_SCENARIOS
    from ._reqs import STEP_PICKING as STEP_PICKING
    from ._reqs import SUBSCENARIOS as SUBSCENARIOS
    from ._reqs import GOTO as GOTO
    from ._reqs import CONFIG_DB as CONFIG_DB
    from ._reqs import MULTIPLE_SCENARIO_EXECUTION as MULTIPLE_SCENARIO_EXECUTION
    from ._reqs import CAMPAIGNS as CAMPAIGNS
    from ._reqs import CAMPAIGN_LOGGING as CAMPAIGN_LOGGING
    from ._reqs import CAMPAIGN_REPORTS as CAMPAIGN_REPORTS
    from ._reqs import ATTRIBUTES as ATTRIBUTES
    from ._reqs import REQUIREMENT_MANAGEMENT as REQUIREMENT_MANAGEMENT
    from ._reqs import REQUIREMENT_MANAGEMENT_REPORTS as REQUIREMENT_MANAGEMENT_REPORTS
    from ._reqs import REQUIREMENT_MANAGEMENT_SCENARIO_CONSOLIDATION as REQUIREMENT_MANAGEMENT_SCENARIO_CONSOLIDATION

# Other reexports.
if True:
    from . import _paths as paths
    from ._reqs import save as save
    from ._tests import setdefaulttestsuites as setdefaulttestsuites
    from ._tools import ensurelicenseheader as ensurelicenseheader
