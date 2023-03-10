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


# The following `try` block avoids IDEs folding the following import lines.
try:
    from ._attributes import ScenarioAttribute as ScenarioAttribute
    import scenario.test._configvalues as _configvalues
    configvalues = _configvalues
    import scenario.test._data as _data
    data = _data
    from ._expectations import ActionResultExpectations as ActionResultExpectations
    from ._expectations import CampaignExpectations as CampaignExpectations
    from ._expectations import ErrorExpectations as ErrorExpectations
    from ._expectations import NOT_SET as NOT_SET
    if typing.TYPE_CHECKING:
        from ._expectations import NotSetType as NotSetType
    from ._expectations import ScenarioExpectations as ScenarioExpectations
    from ._expectations import StatExpectations as StatExpectations
    from ._expectations import StepExpectations as StepExpectations
    from ._expectations import TestSuiteExpectations as TestSuiteExpectations
    import scenario.test._features as _features
    features = _features
    from ._knownissues import IssueLevel as IssueLevel
    import scenario.test._paths as _paths
    paths = _paths
    import scenario.test._reflex as _reflex
    reflex = _reflex
    if typing.TYPE_CHECKING:
        from ._steps import AnyExecutionStepType as AnyExecutionStepType
    from ._steps import ExecutionStep as ExecutionStep
    from ._steps import Step as Step
    from ._steps import VerificationStep as VerificationStep
    from ._subprocess import CampaignSubProcess as CampaignSubProcess
    from ._subprocess import ScenarioSubProcess as ScenarioSubProcess
    from ._subprocess import SubProcess as SubProcess
    from ._testcase import TestCase as TestCase
finally:
    pass
