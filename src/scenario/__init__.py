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


# Imported members, i.e. exported members are not documented by default.
#
# For the purpose, it seems that we should add manually the `:imported-members:` option in the `scenario.rst` output files, which is not convenient
# (see: https://github.com/sphinx-doc/sphinx/issues/4372):
# ```rst
# .. automodule:: scenario
#    :members:
#    :imported-members:
#    :undoc-members:
#    :show-inheritance:
# ```
# For the memo, this resource: https://stackoverflow.com/questions/38765577/overriding-sphinx-autodoc-alias-of-for-import-of-private-class
# also seems to deal with the subject.
#
# That's the reason why we manually document the exported symbols with explicit ReStructuredText as aliases to the inner classes,
# which lets us define documentation sections by the way.

"""
:mod:`scenario` package definition.
"""

# Package management
# ==================

# Inspired from https://packaging.python.org/guides/packaging-namespace-packages/#creating-a-namespace-package
# Define this package as a namespace, so that it can be extended later on (with `scenario.tools`, `scenario.test`, ...).
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

# Used to avoid PEP8 E402 warnings: "Module level import not at top of file" for re-exports below.
__pkg_def = True  # type: bool


# Documentation management
# ========================

# Private constants in this modules are named with double leading underscores
# in order to avoid 'mkdoc.py' list them as an undocumented attribute.


__doc__ += """
Package information
===================
"""

__doc__ += """
.. py:attribute:: info

    Gives the package information: version, ...

    .. seealso:: :attr:`._pkginfo.PackageInfo` implementation.
"""
if __pkg_def:
    from ._pkginfo import PKG_INFO as info  # noqa  ## Constant variable imported as non-constant
    __all__.append("info")


__doc__ += """
Base classes
============

Classes to inherit from in order to describe test scenarios and libraries.
"""

__doc__ += """
.. py:attribute:: Scenario

    Base class to inherit from in order to define a test scenario.

    .. seealso:: :class:`._scenariodefinition.ScenarioDefinition` implementation.

.. py:attribute:: ScenarioDefinition

    Full class name of :class:`Scenario`.
"""
if __pkg_def:
    from ._scenariodefinition import ScenarioDefinition as Scenario
    __all__.append("Scenario")

__doc__ += """
.. py:attribute:: Step

    Base class to inherit from in order to define a test step.

    .. seealso:: :class:`._stepdefinition.StepDefinition` implementation.

.. py:attribute:: StepDefinition
    from ._scenariodefinition import ScenarioDefinition as ScenarioDefinition
    __all__.append("ScenarioDefinition")

    Full class name of :class:`Step`.
"""
if __pkg_def:
    from ._stepdefinition import StepDefinition as Step
    __all__.append("Step")

__doc__ += """
.. py:attribute:: ActionResult

    .. seealso:: :class:`._actionresultdefinition.ActionResultDefinition` implementation.

.. py:attribute:: ActionResultDefinition
    from ._stepdefinition import StepDefinition as StepDefinition
    __all__.append("StepDefinition")

    Full class name of :class:`ActionResult`.
"""
if __pkg_def:
    from ._actionresultdefinition import ActionResultDefinition as ActionResult
    __all__.append("ActionResult")

    from ._actionresultdefinition import ActionResultDefinition as ActionResultDefinition
    __all__.append("ActionResultDefinition")

__doc__ += """
Step sections
=============

Classes that can be used to define step sections.
"""

__doc__ += """
.. py:attribute:: StepSectionDescription

    Step class that holds a description for a section of steps.
    Automatically instanciated by :meth:`._scenariodefinition.ScenarioDefinition.section()`.

    .. seealso:: :class:`._stepsection.StepSectionDescription` implementation.
"""
if __pkg_def:
    from ._stepsection import StepSectionDescription as StepSectionDescription
    __all__.append("StepSectionDescription")

__doc__ += """
.. py:attribute:: StepSectionBegin

    Step class to inherit from, then add in a scenario, in order to define the beginning of a step section.

    .. seealso:: :class:`._stepsection.StepSectionBegin` implementation.
"""
if __pkg_def:
    from ._stepsection import StepSectionBegin as StepSectionBegin
    __all__.append("StepSectionBegin")

__doc__ += """
.. py:attribute:: StepSectionEnd

    Type of the :attr:`._stepsection.StepSectionBegin.end` step to add at the end of a step section.

    .. seealso:: :class:`._stepsection.StepSectionEnd` implementation.
"""
if __pkg_def:
    from ._stepsection import StepSectionEnd as StepSectionEnd
    __all__.append("StepSectionEnd")


__doc__ += """
Assertions
==========

Make verifications on data.
"""

__doc__ += """
.. py:attribute:: Assertions

    Library of static assertion methods.

    Can be sub-classed.
    :class:`Scenario` and :class:`Step` inherit from this class.

    .. seealso:: :class:`._assertions.Assertions` implementation.
"""
if __pkg_def:

__doc__ += """
.. py:attribute:: assertionhelpers

    Helper functions and types when you want to write your own assertion routines.
    from ._assertions import Assertions as Assertions
    __all__.append("Assertions")

    .. seealso:: :mod:`._assertionhelpers` implementation.
"""
if __pkg_def:
    # Note:
    # It seems we can't reexport `assertionhelpers` from the '_assertions.py' module, otherwise it causes failures with mypy...
    # Let's reexport `assertionhelpers` directly from the '_assertions.py' source module.
    from . import _assertionhelpers as assertionhelpers
    __all__.append("assertionhelpers")


__doc__ += """
Logging
=======

Logging management.
"""

__doc__ += """
.. py:attribute:: Logger

    Object with logging capabilities.

    :class:`Scenario` and :class:`Step` inherit from this class.

    .. seealso:: :class:`._logger.Logger` implementation.
"""
if __pkg_def:

__doc__ += """
.. py:attribute:: logging
    from ._logger import Logger as Logger
    __all__.append("Logger")

    Main logger instance.
"""
if __pkg_def:

__doc__ += """
.. py:attribute:: Console

    Console colors.
    from ._loggermain import MAIN_LOGGER as logging  # noqa  ## Constant variable imported as non-constant
    __all__.append("logging")

    .. seealso:: :class:`._console.Console` implementation.
"""
if __pkg_def:
    from ._console import Console as Console
    __all__.append("Console")

__doc__ += """
.. py:attribute:: LogExtraData

    Logging extra data management.

    .. seealso:: :class:`._logextradata.LogExtraData` implementation.
"""
if __pkg_def:
    from ._logextradata import LogExtraData as LogExtraData
    __all__.append("LogExtraData")

__doc__ += """
.. py:attribute:: debug

    Helper functions and types for debugging.

    .. seealso:: :mod:`._debugutils` implementation.
"""
if __pkg_def:
    from . import _debugutils as debug
    __all__.append("debug")


__doc__ += """
Configuration
=============

Configuration management.
"""

__doc__ += """
.. py:attribute:: conf

    Configuration manager instance.

    .. seealso:: :class:`._configdb.ConfigDatabase` implemenation.
"""
if __pkg_def:

__doc__ += """
.. py:attribute:: ConfigNode
    from ._configdb import CONFIG_DB as conf  # noqa  ## Constant variable imported as non-constant
    __all__.append("conf")

    .. seealso:: :class:`._confignode.ConfigNode` implementation.
"""
if __pkg_def:
    from ._confignode import ConfigNode as ConfigNode
    __all__.append("ConfigNode")

__doc__ += """
.. py:attribute:: ConfigKey

    `scenario` configuration keys.

    .. seealso:: :class:`._scenarioconfig.ScenarioConfig.Key` implementation.
"""
if __pkg_def:
    # Note: Can't re-export `ScenarioConfig.Key` as `ConfigKey` with a single `import` statement. Use an intermediate private instance.
    from ._scenarioconfig import ScenarioConfig as _ScenarioConfig
    ConfigKey = _ScenarioConfig.Key
    __all__.append("ConfigKey")


__doc__ += """
Launchers
=========

Classes to launch the test scenarios and campaigns from custom launcher scripts.
"""

__doc__ += """
.. py:attribute:: runner

    Scenario runner instance.

    Call from your own scenario launcher script with:

    .. code-block:: python

        scenario.runner.main()

    .. seealso:: :class:`._scenariorunner.ScenarioRunner` implementation.
"""
if __pkg_def:

__doc__ += """
.. py:attribute:: campaign_runner

    Campaign runner instance.

    Call from your own campaign launcher script with:

    .. code-block:: python

        scenario.campaign_runner.main()
    from ._scenariorunner import SCENARIO_RUNNER as runner  # noqa  ## Constant variable imported as non-constant
    __all__.append("runner")

    .. seealso:: :class:`._campaignrunner.CampaignRunner` implementation.
"""
if __pkg_def:

__doc__ += """
.. py:attribute:: Args

    Base class for :class:`ScenarioArgs` and :class:`CampaignArgs`.

    .. seealso:: :class:`._args.Args` implementation.
"""
if __pkg_def:

__doc__ += """
.. py:attribute:: ScenarioArgs
    from ._campaignrunner import CAMPAIGN_RUNNER as campaign_runner  # noqa  ## Constant variable imported as non-constant
    __all__.append("campaign_runner")

    Inherit from this class in order to extend :class:`._scenariorunner.ScenarioRunner` arguments with your own launcher script ones.
    from ._args import Args as Args
    __all__.append("Args")

    .. seealso:: :class:`._scenarioargs.ScenarioArgs` implementation.
"""
if __pkg_def:
    from ._scenarioargs import ScenarioArgs as ScenarioArgs
    __all__.append("ScenarioArgs")

__doc__ += """
.. py:attribute:: CampaignArgs

    Inherit from this class in order to extend :class:`._campaignrunner.CampaignRunner` arguments with your own launcher script ones.

    .. seealso:: :class:`._campaignargs.CampaignArgs` implementation.
"""
if __pkg_def:
    from ._campaignargs import CampaignArgs as CampaignArgs
    __all__.append("CampaignArgs")

__doc__ += """
.. py:attribute:: ErrorCode

    Error codes returned by :meth:`._scenariorunner.ScenarioRunner.main()` and :meth:`._campaignrunner.CampaignRunner.main()`.

    .. seealso:: :class:`._errcodes.ErrorCode` implementation.
"""
if __pkg_def:
    from ._errcodes import ErrorCode as ErrorCode
    __all__.append("ErrorCode")


__doc__ += """
Handlers (advanced)
===================

Add reactive code.
"""

__doc__ += """
.. py:attribute:: handlers

    Handler manager instance.

    .. seealso:: :class:`._handlers.Handlers` implementation.
"""
if __pkg_def:
    from ._handlers import HANDLERS as handlers  # noqa  ## Constant variable imported as non-constant
    __all__.append("handlers")

__doc__ += """
.. py:attribute:: Event

    .. seealso:: :class:`._scenarioevents.ScenarioEvent` implementation.
"""
if __pkg_def:

__doc__ += """
.. py:attribute:: EventData
    from ._scenarioevents import ScenarioEvent as Event
    __all__.append("Event")

    .. seealso:: :class:`._scenarioevents.ScenarioEventData` implementation.
"""
if __pkg_def:
    from ._scenarioevents import ScenarioEventData as EventData
    __all__.append("EventData")


__doc__ += """
Execution result classes (advanced)
===================================

Sometimes, you may need to access information about the test execution itself.
"""

__doc__ += """
.. py:attribute:: ExecutionStatus

    Describes the final status of a scenario or campaign execution.

    .. seealso:: :class:`._executionstatus.ExecutionStatus` implementation.
"""
if __pkg_def:
    from ._executionstatus import ExecutionStatus as ExecutionStatus
    __all__.append("ExecutionStatus")

__doc__ += """
.. py:attribute:: ScenarioExecution

    .. seealso:: :class:`._scenarioexecution.ScenarioExecution` implementation.
"""
if __pkg_def:
    from ._scenarioexecution import ScenarioExecution as ScenarioExecution
    __all__.append("ScenarioExecution")

__doc__ += """
.. py:attribute:: StepExecution

    .. seealso:: :class:`._stepexecution.StepExecution` implementation.
"""
if __pkg_def:
    from ._stepexecution import StepExecution as StepExecution
    __all__.append("StepExecution")

__doc__ += """
.. py:attribute:: ActionResultExecution

    .. seealso:: :class:`._actionresultexecution.ActionResultExecution` implementation.
"""
if __pkg_def:
    from ._actionresultexecution import ActionResultExecution as ActionResultExecution
    __all__.append("ActionResultExecution")

__doc__ += """
.. py::attribute:: CampaignExecution

    .. seealso:: :class:`._campaignexecutions.CampaignExecution` implementation.
"""
if __pkg_def:
    from ._campaignexecution import CampaignExecution as CampaignExecution
    __all__.append("CampaignExecution")

__doc__ += """
.. py::attribute:: TestSuiteExecution

    .. seealso:: :class:`._campaignexecutions.TestSuiteExecution` implementation.
"""
if __pkg_def:
    from ._campaignexecution import TestSuiteExecution as TestSuiteExecution
    __all__.append("TestSuiteExecution")

__doc__ += """
.. py::attribute:: TestCaseExecution

    .. seealso:: :class:`._campaignexecutions.TestCaseExecution` implementation.
"""
if __pkg_def:
    from ._campaignexecution import TestCaseExecution as TestCaseExecution
    __all__.append("TestCaseExecution")

__doc__ += """
.. py:attribute:: TestError

    Base class that describes an error that occurred during the tests.

    .. seealso:: :class:`._testerrors.TestError` implementation.
"""
if __pkg_def:
    from ._testerrors import TestError as TestError
    __all__.append("TestError")

__doc__ += """
.. py:attribute:: ExceptionError

    Subclass of :class:`TestError` that describes an error due to an exception that occurred during the tests.

    .. seealso:: :class:`._testerrors.ExceptionError` implementation.
"""
if __pkg_def:
    from ._testerrors import ExceptionError as ExceptionError
    __all__.append("ExceptionError")

__doc__ += """
.. py:attribute:: KnownIssue

    Subclass of :class:`TestError` that describes an error due to an exception that occurred during the tests.

    .. seealso:: :class:`._knownissues.KnownIssue` implementation.
"""
if __pkg_def:
    from ._knownissues import KnownIssue as KnownIssue
    __all__.append("KnownIssue")

__doc__ += """
.. py:attribute:: IssueLevel

    Provides methods to define named issue levels.

    .. seealso:: :class:`._issuelevels.IssueLevel` implementation.

.. py:attribute:: AnyIssueLevelType

    .. seealso:: :class:`._issuelevels.AnyIssueLevelType` implementation.
"""
if __pkg_def:
    from ._issuelevels import IssueLevel as IssueLevel
    __all__.append("IssueLevel")
if typing.TYPE_CHECKING:
    from ._issuelevels import AnyIssueLevelType as AnyIssueLevelType
    __all__.append("AnyIssueLevelType")

__doc__ += """
.. py:attribute:: TimeStats

    Describes execution time statistics.

    .. seealso:: :class:`._stats.TimeStats` implementation.
"""
if __pkg_def:
    from ._stats import TimeStats as TimeStats
    __all__.append("TimeStats")

__doc__ += """
.. py:attribute:: ExecTotalStats

    Describes count statistics: number of items executed, out of the total number of items.

    .. seealso:: :class:`._stats.ExecTotalStats` implementation.
"""
if __pkg_def:
    from ._stats import ExecTotalStats as ExecTotalStats
    __all__.append("ExecTotalStats")

__doc__ += """
.. py:attribute:: stack

    Scenario stack instance.

    .. seealso:: :class:`._scenariostack.ScenarioStack` implementation.
"""
if __pkg_def:
    from ._scenariostack import SCENARIO_STACK as stack  # noqa  ## Constant variable imported as non-constant
    __all__.append("stack")


__doc__ += """
Reports (advanced)
==================

The following objects give you the opportunity to read and write scenario and campaign reports.
"""

__doc__ += """
.. py:attribute:: report

    Scenario report manager.

    .. seealso:: :class:`._scenarioreport.ScenarioReport` implementation.
"""
if __pkg_def:

__doc__ += """
.. py:attribute:: campaign_report

    Campaign report manager.
    from ._scenarioreport import SCENARIO_REPORT as report  # noqa  ## Constant variable imported as non-constant
    __all__.append("report")

    .. seealso:: :class:`._campaignreport.CampaignReport` implementation.
"""
if __pkg_def:
    from ._campaignreport import CAMPAIGN_REPORT as campaign_report  # noqa  ## Constant variable imported as non-constant
    __all__.append("campaign_report")


__doc__ += """
Miscellaneous
=============
"""

__doc__ += """
.. py:attribute:: Path

    .. seealso:: :class:`._path.Path` implementation.

.. py:attribute:: AnyPathType

    .. seealso:: :class:`._path.AnyPathType` implementation.
"""
if __pkg_def:
    from ._path import Path as Path
    __all__.append("Path")
if typing.TYPE_CHECKING:
    from ._path import AnyPathType as AnyPathType
    __all__.append("AnyPathType")

__doc__ += """
.. py:attribute:: SubProcess

    Eases the way to prepare a sub-process, execute it, and then retrieve its results.

    .. seealso:: :class:`._subprocess.SubProcess` implementation.

.. py:attribute:: VarSubProcessType

    .. seealso:: :class:`._subprocess.VarSubProcessType` implementation.
"""
if __pkg_def:
    from ._subprocess import SubProcess as SubProcess
    __all__.append("SubProcess")
if typing.TYPE_CHECKING:
    from ._subprocess import VarSubProcessType as VarSubProcessType
    __all__.append("VarSubProcessType")

__doc__ += """
.. py:attribute:: CodeLocation

    .. seealso:: :class:`._locations.CodeLocation` implementation.
"""
if __pkg_def:
    from ._locations import CodeLocation as CodeLocation
    __all__.append("CodeLocation")

__doc__ += """
.. py:attribute:: datetime

    Date/time utils.

    .. seealso:: :mod:`._datetimeutils` implementation.
"""
if __pkg_def:
    from . import _datetimeutils as datetime
    __all__.append("datetime")

__doc__ += """
.. py:attribute:: tz

    Timezone utils.

    .. seealso:: :mod:`._timezoneutils` implementation.
"""
if __pkg_def:
    from . import _timezoneutils as timezone
    __all__.append("timezone")

__doc__ += """
.. py:attribute:: enum

    Enum utils.

    .. seealso:: :mod:`._enumutils` implementation.
"""
if __pkg_def:
    from . import _enumutils as enum
    __all__.append("enum")


# Since the implementation is done in private modules,
# Sphinx will put implementation documentation at the end of the `scenario` documentation page.
# Finish with the title below, as an introduction to it.
__doc__ += """
Implementation
==============
"""
