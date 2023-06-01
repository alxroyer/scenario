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


if True:
    # Package dependencies.
    from ._pkgdeps import checkpkgdeps as _checkpkgdeps
    _checkpkgdeps()

# The `try` block below avoids IDEs folding the following import lines.
try:
    # Reexports.
    from ._attributes import ScenarioAttribute as ScenarioAttribute
    from . import _configvalues as configvalues
    from . import _data as data
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
    from . import _features as features
    from ._knownissues import IssueLevel as IssueLevel
    from . import _paths as paths
    from . import _reflection as reflection
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
