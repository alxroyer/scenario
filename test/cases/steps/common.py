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
This module intends to provide shortcuts to common steps for test cases.

.. warning:: Do not import this module from other step modules, otherwise it could end in cyclic module dependencies.
"""

# The `try` block below avoids IDEs folding the following import lines.
try:
    # Common steps:
    from jsonreport.steps.expectations import CheckJsonReportExpectations as CheckJsonReportExpectations
    from multiplescenarios.steps.expectations import CheckFinalResultsLogExpectations as CheckFinalResultsLogExpectations
    from multiplescenarios.steps.parser import ParseFinalResultsLog as ParseFinalResultsLog
    from scenarioexecution.steps.execution import ExecScenario as ExecScenario
    from scenariologging.steps.expectations import CheckScenarioLogExpectations as CheckScenarioLogExpectations
    from scenariologging.steps.parser import ParseScenarioLog as ParseScenarioLog
    from steps.commonargs import ExecCommonArgs as ExecCommonArgs
    from steps.logverifications import LogVerificationStep as LogVerificationStep
finally:
    pass
