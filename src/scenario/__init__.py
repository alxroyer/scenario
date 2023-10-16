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
:mod:`scenario` package definition.
"""

# Package management
# ==================

# Inspired from https://packaging.python.org/guides/packaging-namespace-packages/#creating-a-namespace-package
# Define this package as a namespace, so that it can be extended later on (with `scenario.tools`, `scenario.test`, ...).
#
# Memo:
# Don't try to fix `__path__` prior to making the `pkgutil.extend_path()` call below, nor catch a potential `NameError`,
# otherwise IDEs may get confused with `scenario.test`, `scenario.tools`, ... extensions.
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)  # noqa  ## Name '__path__' can be undefined


# System imports
# ==============

# Make system imports after the namespace definition above.
import typing


# Export management
# =================

# Explicit export declarations (see https://docs.python.org/3/tutorial/modules.html#importing-from-a-package).
__all__ = []  # type: typing.List[str]


# Documentation management
# ========================

# Private constants in this modules are named with double leading underscores
# in order to avoid 'mkdoc.py' list them as an undocumented attribute.

# As introduced in 'doc/src/devel.coding-rules.doc.rst',
# we choose to disable member documentation for this module ('doc/src/py/scenario.rst' fixed after `sphinx-apidoc` execution),
# and document exported symbols with explicit `.. py:attribute::` directives in the docstring of this module.


__doc__ += """
Package information
===================
"""

if True:
    __doc__ += """
    .. py:attribute:: info

        Gives the package information: version, ...

        .. seealso:: :class:`._pkginfo.PackageInfo` implementation.
    """
    from ._pkginfo import PKG_INFO as info  # noqa  ## Constant variable imported as non-constant
    __all__.append("info")


__doc__ += """
Base classes
============

Classes that define a test scenario.
"""

if True:
    __doc__ += """
    .. py:attribute:: Scenario

        Base class to inherit from in order to define a test scenario.

        .. seealso:: :class:`._scenariodefinition.ScenarioDefinition` implementation.
    """
    from ._scenariodefinition import ScenarioDefinition as Scenario
    __all__.append("Scenario")

    __doc__ += """
    .. py:attribute:: ScenarioDefinition

        Full class name of :class:`Scenario`.
    """
    from ._scenariodefinition import ScenarioDefinition as ScenarioDefinition
    __all__.append("ScenarioDefinition")

if True:
    __doc__ += """
    .. py:attribute:: Step

        Base class to inherit from in order to define a test step
        (see :ref:`step objects <step-objects>`).

        .. seealso:: :class:`._stepdefinition.StepDefinition` implementation.
    """
    from ._stepdefinition import StepDefinition as Step
    __all__.append("Step")

    __doc__ += """
    .. py:attribute:: StepDefinition

        Full class name of :class:`Step`.
    """
    from ._stepdefinition import StepDefinition as StepDefinition
    __all__.append("StepDefinition")

if True:
    __doc__ += """
    .. py:attribute:: ActionResult

        Each action / expected result creates an instance of this class
        (you should not inherit from it normally).

        .. seealso:: :class:`._actionresultdefinition.ActionResultDefinition` implementation.
    """
    from ._actionresultdefinition import ActionResultDefinition as ActionResult
    __all__.append("ActionResult")

    __doc__ += """
    .. py:attribute:: ActionResultDefinition

        Full class name of :class:`ActionResult`.
    """
    from ._actionresultdefinition import ActionResultDefinition as ActionResultDefinition
    __all__.append("ActionResultDefinition")


__doc__ += """
Step sections
=============

Once you have opted for :ref:`step objects <step-objects>`,
classes that can be used to define :ref:`step sections <step-sections>`.
"""

if True:
    __doc__ += """
    .. py:attribute:: StepSectionDescription

        Step class that holds a description for a section of steps.
        Automatically instanciated by :meth:`._scenariodefinition.ScenarioDefinition.section()`.

        .. seealso:: :class:`._stepsection.StepSectionDescription` implementation.
    """
    from ._stepsection import StepSectionDescription as StepSectionDescription
    __all__.append("StepSectionDescription")

if True:
    __doc__ += """
    .. py:attribute:: StepSectionBegin

        Step class to inherit from, then add in a scenario, in order to define the beginning of a step section.

        .. seealso:: :class:`._stepsection.StepSectionBegin` implementation.
    """
    from ._stepsection import StepSectionBegin as StepSectionBegin
    __all__.append("StepSectionBegin")

    __doc__ += """
    .. py:attribute:: StepSectionEnd

        Type of the :attr:`._stepsection.StepSectionBegin.end` step to add at the end of a step section.

        .. seealso:: :class:`._stepsection.StepSectionEnd` implementation.
    """
    from ._stepsection import StepSectionEnd as StepSectionEnd
    __all__.append("StepSectionEnd")


__doc__ += """
Step specifications
===================

Step specifications may be useful to refer to a given step
when using the :ref:`goto feature <goto>` or :ref:`assertions routines <assertions>` about step execution times.
"""

if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: AnyStepDefinitionSpecificationType

        Various ways to refer to a step definition.

        .. seealso:: :obj:`._stepspecifications.AnyStepDefinitionSpecificationType` implementation.
    """
    from ._stepspecifications import AnyStepDefinitionSpecificationType as AnyStepDefinitionSpecificationType
    __all__.append("AnyStepDefinitionSpecificationType")

if True:
    __doc__ += """
    .. py:attribute:: StepDefinitionSpecification

        Implementation class for :obj:`AnyStepDefinitionSpecificationType`.

        .. seealso:: :class:`._stepspecifications.StepDefinitionSpecification` implementation.
    """
    from ._stepspecifications import StepDefinitionSpecification as StepDefinitionSpecification
    __all__.append("StepDefinitionSpecification")

if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: AnyStepExecutionSpecificationType

        Various ways to refer to a step execution.

        .. seealso:: :obj:`._stepspecifications.AnyStepExecutionSpecificationType` implementation.
    """
    from ._stepspecifications import AnyStepExecutionSpecificationType as AnyStepExecutionSpecificationType
    __all__.append("AnyStepExecutionSpecificationType")

if True:
    __doc__ += """
    .. py:attribute:: StepExecutionSpecification

        Implementation class for :obj:`AnyStepExecutionSpecificationType`.

        .. seealso:: :class:`._stepspecifications.StepExecutionSpecification` implementation.
    """
    from ._stepspecifications import StepExecutionSpecification as StepExecutionSpecification
    __all__.append("StepExecutionSpecification")


__doc__ += """
Assertions
==========

:ref:`Assertions` can be used from :class:`Scenario` and :class:`Step` classes,
or in :ref:`test libraries <test-libs>`.

Assertion routines also provide an easy way to collect :ref:`evidence <evidence>`.
"""

if True:
    __doc__ += """
    .. py:attribute:: Assertions

        Library of static assertion methods.

        Can be subclassed.
        :class:`Scenario` and :class:`Step` inherit from this class.

        .. seealso:: :class:`._assertions.Assertions` implementation.
    """
    from ._assertions import Assertions as Assertions
    __all__.append("Assertions")

if True:
    __doc__ += """
    .. py:attribute:: assertionhelpers

        Helper functions and types when you want to write your own assertion routines.

        .. seealso:: :mod:`._assertionhelpers` implementation.
    """
    # Note:
    # It seems we can't reexport `assertionhelpers` from the '_assertions.py' module, otherwise it causes failures with mypy...
    # Let's reexport `assertionhelpers` directly from the '_assertions.py' source module.
    from . import _assertionhelpers as assertionhelpers
    __all__.append("assertionhelpers")


__doc__ += """
Known issues
============

Track :ref:`known issues <known-issues>` instead of letting tests fail with unqualified errors.
"""

if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: AnyIssueLevelType

        ``int`` or ``enum.Enum`` that describes an issue level.

        .. seealso:: :obj:`._issuelevels.AnyIssueLevelType` implementation.
    """
    from ._issuelevels import AnyIssueLevelType as AnyIssueLevelType
    __all__.append("AnyIssueLevelType")

if True:
    __doc__ += """
    .. py:attribute:: IssueLevel

        Abstract class that provides methods to define named issue levels.

        .. seealso:: :class:`._issuelevels.IssueLevel` implementation.
    """
    from ._issuelevels import IssueLevel as IssueLevel
    __all__.append("IssueLevel")


__doc__ += """
Logging
=======

Use `scenario` :ref:`logging facilities <logging>` to facilitate test execution analyses.
"""

if True:
    __doc__ += """
    .. py:attribute:: Logger

        Object with logging capabilities.

        :class:`Scenario` and :class:`Step` inherit from this class.

        .. seealso:: :class:`._logger.Logger` implementation.
    """
    from ._logger import Logger as Logger
    __all__.append("Logger")

if True:
    __doc__ += """
    .. py:attribute:: logging

        Main logger instance.

        .. seealso:: :data:`._loggermain.MAIN_LOGGER` implementation.
    """
    from ._loggermain import MAIN_LOGGER as logging  # noqa  ## Constant variable imported as non-constant
    __all__.append("logging")

if True:
    __doc__ += """
    .. py:attribute:: LoggingContext

        Logging context.

        .. seealso:: :class:`._loggingcontext.LoggingContext` implementation.
    """
    from ._loggingcontext import LoggingContext as LoggingContext

if True:
    __doc__ += """
    .. py:attribute:: Console

        Console colors.

        .. seealso:: :class:`._console.Console` implementation.
    """
    from ._console import Console as Console
    __all__.append("Console")

if True:
    __doc__ += """
    .. py:attribute:: LogExtraData

        Logging extra data management.

        .. seealso:: :class:`._logextradata.LogExtraData` implementation.
    """
    from ._logextradata import LogExtraData as LogExtraData
    __all__.append("LogExtraData")

if True:
    __doc__ += """
    .. py:attribute:: debug

        Helper functions and types for debugging.

        .. seealso:: :mod:`._debugutils` implementation.
    """
    from . import _debugutils as debug
    __all__.append("debug")


__doc__ += """
Configuration
=============

Modulate test executions thanks to the `scenario` :ref:`open configuration database <config-db>`.
"""

if True:
    __doc__ += """
    .. py:attribute:: conf

        Configuration manager instance.

        .. seealso:: :class:`._configdb.ConfigDatabase` implementation.
    """
    from ._configdb import CONFIG_DB as conf  # noqa  ## Constant variable imported as non-constant
    __all__.append("conf")

if True:
    __doc__ += """
    .. py:attribute:: ConfigNode

        .. seealso:: :class:`._confignode.ConfigNode` implementation.
    """
    from ._confignode import ConfigNode as ConfigNode
    __all__.append("ConfigNode")

if True:
    __doc__ += """
    .. py:attribute:: ConfigKey

        `scenario` configuration keys.

        .. seealso:: :class:`._scenarioconfig.ScenarioConfig.Key` implementation.
    """
    # Note: Can't reexport `ScenarioConfig.Key` as `ConfigKey` with a single `import` statement. Use an intermediate private instance.
    from ._scenarioconfig import ScenarioConfig as _ScenarioConfig
    ConfigKey = _ScenarioConfig.Key
    __all__.append("ConfigKey")


__doc__ += """
Launchers
=========

Classes for launching test scenarios and campaigns from :ref:`custom launcher scripts <launcher>`.
"""

if True:
    __doc__ += """
    .. py:attribute: runner

        Scenario runner instance.

        Call from your own scenario launcher script with:

        .. code-block:: python

            scenario.runner.main()

        .. seealso:: :class:`._scenariorunner.ScenarioRunner` implementation.
    """
    from ._scenariorunner import SCENARIO_RUNNER as runner  # noqa  ## Constant variable imported as non-constant
    __all__.append("runner")

if True:
    __doc__ += """
    .. py:attribute:: campaign_runner

        Campaign runner instance.

        Call from your own campaign launcher script with:

        .. code-block:: python

            scenario.campaign_runner.main()

        .. seealso:: :class:`._campaignrunner.CampaignRunner` implementation.
    """
    from ._campaignrunner import CAMPAIGN_RUNNER as campaign_runner  # noqa  ## Constant variable imported as non-constant
    __all__.append("campaign_runner")

if True:
    __doc__ += """
    .. py:attribute:: Args

        Base class for :class:`ScenarioArgs` and :class:`CampaignArgs`.

        .. seealso:: :class:`._args.Args` implementation.
    """
    from ._args import Args as Args
    __all__.append("Args")

if True:
    __doc__ += """
    .. py:attribute:: ScenarioArgs

        Inherit from this class in order to extend :class:`._scenariorunner.ScenarioRunner` arguments with your own launcher script ones.

        .. seealso:: :class:`._scenarioargs.ScenarioArgs` implementation.
    """
    from ._scenarioargs import ScenarioArgs as ScenarioArgs
    __all__.append("ScenarioArgs")

if True:
    __doc__ += """
    .. py:attribute:: CampaignArgs

        Inherit from this class in order to extend :class:`._campaignrunner.CampaignRunner` arguments with your own launcher script ones.

        .. seealso:: :class:`._campaignargs.CampaignArgs` implementation.
    """
    from ._campaignargs import CampaignArgs as CampaignArgs
    __all__.append("CampaignArgs")

if True:
    __doc__ += """
    .. py:attribute:: ErrorCode

        Error codes returned by :meth:`._scenariorunner.ScenarioRunner.main()` and :meth:`._campaignrunner.CampaignRunner.main()`.

        .. seealso:: :class:`._errcodes.ErrorCode` implementation.
    """
    from ._errcodes import ErrorCode as ErrorCode
    __all__.append("ErrorCode")

if True:
    __doc__ += """
    .. py:attribute:: ErrorCodeError

        Exception holding an :class:`ErrorCode` value.

        .. seealso:: :class:`_errcodes.ErrorCodeError` implementation.
    """
    from ._errcodes import ErrorCodeError as ErrorCodeError
    __all__.append("ErrorCodeError")


__doc__ += """
Handlers
========

Register :ref:`handlers <handlers>` for reactive code to be called on events.
"""

if True:
    __doc__ += """
    .. py:attribute:: handlers

        Handler manager instance.

        .. seealso:: :class:`._handlers.Handlers` implementation.
    """
    from ._handlers import HANDLERS as handlers  # noqa  ## Constant variable imported as non-constant
    __all__.append("handlers")

if True:
    __doc__ += """
    .. py:attribute:: Event

        `scenario` events that can be triggered.

        .. seealso:: :class:`._scenarioevents.ScenarioEvent` implementation.
    """
    from ._scenarioevents import ScenarioEvent as Event
    __all__.append("Event")

if True:
    __doc__ += """
    .. py:attribute:: EventData

        Data classes associated with `scenario` events.

        .. seealso:: :class:`._scenarioevents.ScenarioEventData` implementation.
    """
    from ._scenarioevents import ScenarioEventData as EventData
    __all__.append("EventData")


__doc__ += """
Execution
=========

In certain circumstances (:ref:`launcher scripts <launcher>`, :ref:`handlers <handlers>`, ...),
you may need to access information about test execution.
"""

if True:
    __doc__ += """
    .. py:attribute:: stack

        :ref:`Scenario stack <scenario-stack>` instance.

        .. seealso:: :class:`._scenariostack.ScenarioStack` implementation.
    """
    from ._scenariostack import SCENARIO_STACK as stack  # noqa  ## Constant variable imported as non-constant
    __all__.append("stack")

if True:
    __doc__ += """
    .. py:attribute:: ExecutionStatus

        Describes the final status of a scenario or campaign execution.

        .. seealso:: :class:`._executionstatus.ExecutionStatus` implementation.
    """
    from ._executionstatus import ExecutionStatus as ExecutionStatus
    __all__.append("ExecutionStatus")

if True:
    __doc__ += """
    .. py:attribute:: ScenarioExecution

        .. seealso:: :class:`._scenarioexecution.ScenarioExecution` implementation.
    """
    from ._scenarioexecution import ScenarioExecution as ScenarioExecution
    __all__.append("ScenarioExecution")

if True:
    __doc__ += """
    .. py:attribute:: StepExecution

        .. seealso:: :class:`._stepexecution.StepExecution` implementation.
    """
    from ._stepexecution import StepExecution as StepExecution
    __all__.append("StepExecution")

if True:
    __doc__ += """
    .. py:attribute:: ActionResultExecution

        .. seealso:: :class:`._actionresultexecution.ActionResultExecution` implementation.
    """
    from ._actionresultexecution import ActionResultExecution as ActionResultExecution
    __all__.append("ActionResultExecution")

if True:
    __doc__ += """
    .. py:attribute:: CampaignExecution

        .. seealso:: :class:`._campaignexecution.CampaignExecution` implementation.
    """
    from ._campaignexecution import CampaignExecution as CampaignExecution
    __all__.append("CampaignExecution")

if True:
    __doc__ += """
    .. py:attribute:: TestSuiteExecution

        .. seealso:: :class:`._campaignexecution.TestSuiteExecution` implementation.
    """
    from ._campaignexecution import TestSuiteExecution as TestSuiteExecution
    __all__.append("TestSuiteExecution")

if True:
    __doc__ += """
    .. py:attribute:: TestCaseExecution

        .. seealso:: :class:`._campaignexecution.TestCaseExecution` implementation.
    """
    from ._campaignexecution import TestCaseExecution as TestCaseExecution
    __all__.append("TestCaseExecution")


__doc__ += """
:ref:`Error management <errors>`:
"""

if True:
    __doc__ += """
    .. py:attribute:: TestError

        Base class that describes an error that occurred during the tests.

        .. seealso:: :class:`._testerrors.TestError` implementation.
    """
    from ._testerrors import TestError as TestError
    __all__.append("TestError")

if True:
    __doc__ += """
    .. py:attribute:: ExceptionError

        Subclass of :class:`TestError` that describes an error due to an exception that occurred during the tests.

        .. seealso:: :class:`._testerrors.ExceptionError` implementation.
    """
    from ._testerrors import ExceptionError as ExceptionError
    __all__.append("ExceptionError")

if True:
    __doc__ += """
    .. py:attribute:: KnownIssue

        Subclass of :class:`TestError` that describes a known issue.

        .. seealso:: :class:`._knownissues.KnownIssue` implementation.
    """
    from ._knownissues import KnownIssue as KnownIssue
    __all__.append("KnownIssue")


__doc__ += """
Statistics:
"""

if True:
    __doc__ += """
    .. py:attribute:: TimeStats

        Describes execution time statistics.

        .. seealso:: :class:`._stats.TimeStats` implementation.
    """
    from ._stats import TimeStats as TimeStats
    __all__.append("TimeStats")

if True:
    __doc__ += """
    .. py:attribute:: ExecTotalStats

        Describes count statistics: number of items executed, out of the total number of items.

        .. seealso:: :class:`._stats.ExecTotalStats` implementation.
    """
    from ._stats import ExecTotalStats as ExecTotalStats
    __all__.append("ExecTotalStats")


__doc__ += """
Reports
=======

The following objects give you the opportunity to read and write :ref:`scenario and campaign reports <reports>`.
"""

if True:
    __doc__ += """
    .. py:attribute:: report

        Scenario report manager.

        .. seealso:: :class:`._scenarioreport.ScenarioReport` implementation.
    """
    from ._scenarioreport import SCENARIO_REPORT as report  # noqa  ## Constant variable imported as non-constant
    __all__.append("report")

if True:
    __doc__ += """
    .. py:attribute:: campaign_report

        Campaign report manager.

        .. seealso:: :class:`._campaignreport.CampaignReport` implementation.
    """
    from ._campaignreport import CAMPAIGN_REPORT as campaign_report  # noqa  ## Constant variable imported as non-constant
    __all__.append("campaign_report")


__doc__ += """
Scenario attributes
===================
"""

if True:
    __doc__ += """
    .. py:attribute:: ScenarioAttributes

        Core scenario attributes.

        .. seealso:: :class:`._scenarioattributes.CoreScenarioAttributes` implementation.
    """
    from ._scenarioattributes import CoreScenarioAttributes as ScenarioAttributes
    __all__.append("ScenarioAttributes")

__doc__ += """
.. seealso:: :meth:`._scenariodefinition.ScenarioDefinition.setattribute()` for user scenario attributes.
"""


__doc__ += """
Requirement management
======================

The scenario framework provide the ability to master the way tests cover input :ref:`requirements <req-mgt>`.
"""

if True:
    __doc__ += """
    .. py:attribute:: Req

        Requirement object.

        .. seealso:: :class:`._req.Req` implementation.
    """
    from ._req import Req as Req
    __all__.append("Req")
if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: AnyReqType

        Any requirement type.

        .. seealso:: :obj:`._reqtypes.AnyReqType` implementation.
    """
    from ._reqtypes import AnyReqType as AnyReqType
    __all__.append("AnyReqType")

if True:
    __doc__ += """
    .. py:attribute:: ReqRef

        Requirement reference.

        .. seealso:: :class:`._reqref.ReqRef` implementation.
    """
    from ._reqref import ReqRef as ReqRef
    __all__.append("ReqRef")
if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: AnyReqRefType

        Any requirement reference type.

        .. seealso:: :obj:`._reqtypes.AnyReqRefType` implementation.
    """
    from ._reqtypes import AnyReqRefType as AnyReqRefType
    __all__.append("AnyReqRefType")

if True:
    __doc__ += """
    .. py:attribute:: req_db

        Requirement database.

        .. seealso:: :class:`._reqdb.ReqDatabase` implementation.
    """
    from ._reqdb import REQ_DB as req_db  # noqa  ## Constant variable imported as non-constant
    __all__.append("req_db")

if True:
    __doc__ += """
    .. py:attribute:: req_mgt

        Requirement management runner.

        .. seealso:: :class:`._reqmgt.ReqManagement` implementation.
    """
    from ._reqmgtmain import REQ_MANAGEMENT as req_mgt  # noqa  ## Constant variable imported as non-constant
    __all__.append("req_mgt")

if True:
    __doc__ += """
    .. py:attribute:: ReqVerifier

        Requirement verifier class.

        .. note::
            Only :class:`Scenario` and :class:`Step` may verify requirements.

        .. seealso:: :class:`._reqverifier.ReqVerifier` implementation.
    """
    from ._reqverifier import ReqVerifier as ReqVerifier
    __all__.append("ReqVerifier")

if True:
    __doc__ += """
    .. py:attribute:: ReqLink

        Requirement link between a :class:`ReqRef` and one or more :class:`ReqVerifier` objects (:class:`Scenario` or :class:`Step`).

        .. seealso:: :class:`._reqlink.ReqLink` implementation.
    """
    from ._reqlink import ReqLink as ReqLink
    __all__.append("ReqLink")
if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: AnyReqLinkType

        Any kind of requirement link, :class:`ReqLink` included.

        .. seealso:: :obj:`._reqtypes.AnyReqLinkType` implementation.
    """
    from ._reqtypes import AnyReqLinkType as AnyReqLinkType
    __all__.append("AnyReqLinkType")
if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: SetWithReqLinksType

        Set of items with related requirement links.

        .. seealso:: :obj:`._reqtypes.SetWithReqLinksType` implementation.
    """
    from ._reqtypes import SetWithReqLinksType as SetWithReqLinksType
    __all__.append("SetWithReqLinksType")


__doc__ += """
Miscellaneous
=============

The `scenario` framework also exposes a couple of useful classes and types that may be used.
"""

if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: types

        Useful types.

        .. seealso:: :mod:`._types` implementation.
    """
    from . import _types as types
    __all__.append("types")

if True:
    __doc__ += """
    .. py:attribute:: Path

        ``pathlib.Path`` augmentation:

        - absolute / relative paths disambiguation,
        - pretty displays inside a project root path.

        .. seealso:: :class:`._path.Path` implementation.
    """
    from ._path import Path as Path
    __all__.append("Path")
if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: AnyPathType

        Any kind of path, :class:`Path` included.

        .. seealso:: :obj:`._path.AnyPathType` implementation.
    """
    from ._path import AnyPathType as AnyPathType
    __all__.append("AnyPathType")

if True:
    __doc__ += """
    .. py:attribute:: SubProcess

        Eases the way to prepare a sub-process, execute it, and retrieve its results.

        .. seealso:: :class:`._subprocess.SubProcess` implementation.
    """
    from ._subprocess import SubProcess as SubProcess
    __all__.append("SubProcess")
if typing.TYPE_CHECKING:
    __doc__ += """
    .. py:attribute:: VarSubProcessType

        Variable subprocess type, :class:`SubProcess` and subclasses.

        .. seealso:: :obj:`._subprocess.VarSubProcessType` implementation.
    """
    from ._subprocess import VarSubProcessType as VarSubProcessType
    __all__.append("VarSubProcessType")

if True:
    __doc__ += """
    .. py:attribute:: CodeLocation

        .. seealso:: :class:`._locations.CodeLocation` implementation.
    """
    from ._locations import CodeLocation as CodeLocation
    __all__.append("CodeLocation")

if True:
    __doc__ += """
    .. py:attribute:: datetime

        Date/time utils.

        .. seealso:: :mod:`._datetimeutils` implementation.
    """
    from . import _datetimeutils as datetime
    __all__.append("datetime")

if True:
    __doc__ += """
    .. py:attribute:: timezone

        Timezone utils.

        .. seealso:: :mod:`._timezoneutils` implementation.
    """
    from . import _timezoneutils as timezone
    __all__.append("timezone")

if True:
    __doc__ += """
    .. py:attribute:: enum

        Enum utils.

        .. seealso:: :mod:`._enumutils` implementation.
    """
    from . import _enumutils as enum
    __all__.append("enum")
