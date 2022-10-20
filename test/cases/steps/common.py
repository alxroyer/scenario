# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

# Common steps:
from jsonreport.steps.expectations import CheckJsonReportExpectations
from multiplescenarios.steps.expectations import CheckFinalResultsLogExpectations
from multiplescenarios.steps.parser import ParseFinalResultsLog
from scenarioexecution.steps.execution import ExecScenario
from scenariologging.steps.expectations import CheckScenarioLogExpectations
from scenariologging.steps.parser import ParseScenarioLog
from steps.commonargs import ExecCommonArgs
from steps.logverifications import LogVerificationStep
