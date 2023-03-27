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

# As introduced in 'doc/src/devel.coding-rules.doc.rst',
# we choose to disable member documentation for this module ('doc/src/py/scenario.rst' fixed after `sphinx-apidoc` execution).
# Short descriptions of exported symbols, with cross references to private module documentations, are given in tables instead.
__export_table_start = """
.. list-table::
    :widths: auto
    :header-rows: 1
    :stub-columns: 0

    * -
      - Description
      - Implementation
"""
__export_table_end = ""


__doc__ += """
Package information
===================
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :attr:`info`
      - Gives the package information: version, ...
      - :class:`._pkginfo.PackageInfo`
    """
    from ._pkginfo import PKG_INFO as info  # noqa  ## Constant variable imported as non-constant
    __all__.append("info")

__doc__ += __export_table_end


__doc__ += """
Base classes
============

Classes that define a test scenario.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :class:`Scenario`
      - Base class to inherit from in order to define a test scenario.
      - :class:`._scenariodefinition.ScenarioDefinition`
    """
    from ._scenariodefinition import ScenarioDefinition as Scenario
    __all__.append("Scenario")

    __doc__ += """
    * - :class:`ScenarioDefinition`
      - Full class name of :class:`Scenario`.
      - :class:`._scenariodefinition.ScenarioDefinition`
    """
    from ._scenariodefinition import ScenarioDefinition as ScenarioDefinition
    __all__.append("ScenarioDefinition")

if __pkg_def:
    __doc__ += """
    * - :class:`Step`
      - Base class to inherit from in order to define a test step
        (see :ref:`step objects <step-objects>`).
      - :class:`._stepdefinition.StepDefinition`
    """
    from ._stepdefinition import StepDefinition as Step
    __all__.append("Step")

    __doc__ += """
    * - :class:`StepDefinition`
      - Full class name of :class:`Step`.
      - :class:`._stepdefinition.StepDefinition`
    """
    from ._stepdefinition import StepDefinition as StepDefinition
    __all__.append("StepDefinition")

if __pkg_def:
    __doc__ += """
    * - :class:`ActionResult`
      - Each action / expected result creates an instance of this class
        (you should normally not inherit from it).
      - :class:`._actionresultdefinition.ActionResultDefinition`
    """
    from ._actionresultdefinition import ActionResultDefinition as ActionResult
    __all__.append("ActionResult")

    __doc__ += """
    * - :class:`ActionResultDefinition`
      - Full class name of :class:`ActionResult`.
      - :class:`._actionresultdefinition.ActionResultDefinition`
    """
    from ._actionresultdefinition import ActionResultDefinition as ActionResultDefinition
    __all__.append("ActionResultDefinition")

__doc__ += __export_table_end


__doc__ += """
Step sections
=============

Once you have opted for :ref:`step objects <step-objects>`,
classes that can be used to define :ref:`step sections <step-sections>`.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :class:`StepSectionDescription`
      - Step class that holds a description for a section of steps.
        Automatically instanciated by :meth:`._scenariodefinition.ScenarioDefinition.section()`.
      - :class:`._stepsection.StepSectionDescription`
    """
    from ._stepsection import StepSectionDescription as StepSectionDescription
    __all__.append("StepSectionDescription")

if __pkg_def:
    __doc__ += """
    * - :class:`StepSectionBegin`
      - Step class to inherit from, then add in a scenario, in order to define the beginning of a step section.
      - :class:`._stepsection.StepSectionBegin`
    """
    from ._stepsection import StepSectionBegin as StepSectionBegin
    __all__.append("StepSectionBegin")

    __doc__ += """
    * - :class:`StepSectionEnd`
      - Type of the :attr:`._stepsection.StepSectionBegin.end` step to add at the end of a step section.
      - :class:`._stepsection.StepSectionEnd`
    """
    from ._stepsection import StepSectionEnd as StepSectionEnd
    __all__.append("StepSectionEnd")

__doc__ += __export_table_end


__doc__ += """
Assertions
==========

:ref:`Assertions` can be used from :class:`Scenario` and :class:`Step` classes,
or in :ref:`test libraries <test-libs>`.

Assertion routines also provide an easy way to collect :ref:`evidence <evidence>`.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :class:`Assertions`
      - Library of static assertion methods.

        Can be sub-classed.
        :class:`Scenario` and :class:`Step` inherit from this class.
      - :class:`._assertions.Assertions`
    """
    from ._assertions import Assertions as Assertions
    __all__.append("Assertions")

if __pkg_def:
    __doc__ += """
    * - :attr:`assertionhelpers`
      - Helper functions and types when you want to write your own assertion routines.
      - :mod:`._assertionhelpers`
    """
    # Note:
    # It seems we can't reexport `assertionhelpers` from the '_assertions.py' module, otherwise it causes failures with mypy...
    # Let's reexport `assertionhelpers` directly from the '_assertions.py' source module.
    from . import _assertionhelpers as assertionhelpers
    __all__.append("assertionhelpers")

__doc__ += __export_table_end


__doc__ += """
Known issues
============

Track :ref:`known issues <known-issues>` instead of letting tests fail with unqualified errors.
"""

__doc__ += __export_table_start

if typing.TYPE_CHECKING:
    __doc__ += """
    * - :class:`AnyIssueLevelType`
      - ``int`` or ``enum.Enum`` that describes an issue level.
      - :class:`._issuelevels.AnyIssueLevelType`
    """
    from ._issuelevels import AnyIssueLevelType as AnyIssueLevelType
    __all__.append("AnyIssueLevelType")

if __pkg_def:
    __doc__ += """
    * - :class:`IssueLevel`
      - Abstract class that provides methods to define named issue levels.
      - :class:`._issuelevels.IssueLevel`
    """
    from ._issuelevels import IssueLevel as IssueLevel
    __all__.append("IssueLevel")

__doc__ += __export_table_end


__doc__ += """
Logging
=======

Use `scenario` :ref:`logging facilities <logging>` to facilitate test execution analyses.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :class:`Logger`
      - Object with logging capabilities.

        :class:`Scenario` and :class:`Step` inherit from this class.
      - :class:`._logger.Logger`
    """
    from ._logger import Logger as Logger
    __all__.append("Logger")

if __pkg_def:
    __doc__ += """
    * - :attr:`logging`
      - Main logger instance.
      - :attr:`._loggermain.MAIN_LOGGER`
    """
    from ._loggermain import MAIN_LOGGER as logging  # noqa  ## Constant variable imported as non-constant
    __all__.append("logging")

if __pkg_def:
    __doc__ += """
    * - :class:`Console`
      - Console colors.
      - :class:`._console.Console`
    """
    from ._console import Console as Console
    __all__.append("Console")

if __pkg_def:
    __doc__ += """
    * - :class:`LogExtraData`
      - Logging extra data management.
      - :class:`._logextradata.LogExtraData`
    """
    from ._logextradata import LogExtraData as LogExtraData
    __all__.append("LogExtraData")

if __pkg_def:
    __doc__ += """
    * - :mod:`debug`
      - Helper functions and types for debugging.
      - :mod:`._debugutils`
    """
    from . import _debugutils as debug
    __all__.append("debug")

__doc__ += __export_table_end


__doc__ += """
Configuration
=============

Modulate test executions thanks to the `scenario` :ref:`open configuration database <config-db>`.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :attr:`conf`
      - Configuration manager instance.
      - :class:`._configdb.ConfigDatabase`
    """
    from ._configdb import CONFIG_DB as conf  # noqa  ## Constant variable imported as non-constant
    __all__.append("conf")

if __pkg_def:
    __doc__ += """
    * - :class:`ConfigNode`
      -
      - :class:`._confignode.ConfigNode`
    """
    from ._confignode import ConfigNode as ConfigNode
    __all__.append("ConfigNode")

if __pkg_def:
    __doc__ += """
    * - :class:`ConfigKey`
      - `scenario` configuration keys.
      - :class:`._scenarioconfig.ScenarioConfig.Key`
    """
    # Note: Can't re-export `ScenarioConfig.Key` as `ConfigKey` with a single `import` statement. Use an intermediate private instance.
    from ._scenarioconfig import ScenarioConfig as _ScenarioConfig
    ConfigKey = _ScenarioConfig.Key
    __all__.append("ConfigKey")

__doc__ += __export_table_end


__doc__ += """
Launchers
=========

Classes for launching test scenarios and campaigns from :ref:`custom launcher scripts <launcher>`.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :attr:`runner`
      - Scenario runner instance.

        Call from your own scenario launcher script with:

        .. code-block:: python

            scenario.runner.main()

      - :class:`._scenariorunner.ScenarioRunner`
    """
    from ._scenariorunner import SCENARIO_RUNNER as runner  # noqa  ## Constant variable imported as non-constant
    __all__.append("runner")

if __pkg_def:
    __doc__ += """
    * - :attr:`campaign_runner`
      - Campaign runner instance.

        Call from your own campaign launcher script with:

        .. code-block:: python

            scenario.campaign_runner.main()

      - :class:`._campaignrunner.CampaignRunner`
    """
    from ._campaignrunner import CAMPAIGN_RUNNER as campaign_runner  # noqa  ## Constant variable imported as non-constant
    __all__.append("campaign_runner")

if __pkg_def:
    __doc__ += """
    * - :class:`Args`
      - Base class for :class:`ScenarioArgs` and :class:`CampaignArgs`.
      - :class:`._args.Args`
    """
    from ._args import Args as Args
    __all__.append("Args")

if __pkg_def:
    __doc__ += """
    * - :class:`ScenarioArgs`
      - Inherit from this class in order to extend :class:`._scenariorunner.ScenarioRunner` arguments with your own launcher script ones.
      - :class:`._scenarioargs.ScenarioArgs`
    """
    from ._scenarioargs import ScenarioArgs as ScenarioArgs
    __all__.append("ScenarioArgs")

if __pkg_def:
    __doc__ += """
    * - :class:`CampaignArgs`
      - Inherit from this class in order to extend :class:`._campaignrunner.CampaignRunner` arguments with your own launcher script ones.
      - :class:`._campaignargs.CampaignArgs`
    """
    from ._campaignargs import CampaignArgs as CampaignArgs
    __all__.append("CampaignArgs")

if __pkg_def:
    __doc__ += """
    * - :class:`ErrorCode`
      - Error codes returned by :meth:`._scenariorunner.ScenarioRunner.main()` and :meth:`._campaignrunner.CampaignRunner.main()`.
      - :class:`._errcodes.ErrorCode`
    """
    from ._errcodes import ErrorCode as ErrorCode
    __all__.append("ErrorCode")

__doc__ += __export_table_end


__doc__ += """
Handlers (advanced)
===================

Register :ref:`handlers <handlers>` for reactive code to be called on events.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :attr:`handlers`
      - Handler manager instance.
      - :class:`._handlers.Handlers`
    """
    from ._handlers import HANDLERS as handlers  # noqa  ## Constant variable imported as non-constant
    __all__.append("handlers")

if __pkg_def:
    __doc__ += """
    * - :class:`Event`
      - `scenario` events that can be triggered.
      - :class:`._scenarioevents.ScenarioEvent`
    """
    from ._scenarioevents import ScenarioEvent as Event
    __all__.append("Event")

if __pkg_def:
    __doc__ += """
    * - :class:`EventData`
      - Data classes associated with `scenario` events
      - :class:`._scenarioevents.ScenarioEventData`
    """
    from ._scenarioevents import ScenarioEventData as EventData
    __all__.append("EventData")

__doc__ += __export_table_end


__doc__ += """
Execution (advanced)
====================

In certain circumstances (:ref:`launcher scripts <launcher>`, :ref:`handlers <handlers>`, ...),
you may need to access information about test execution.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :attr:`stack`
      - :ref:`Scenario stack <scenario-stack>` instance.
      - :class:`._scenariostack.ScenarioStack`
    """
    from ._scenariostack import SCENARIO_STACK as stack  # noqa  ## Constant variable imported as non-constant
    __all__.append("stack")

if __pkg_def:
    __doc__ += """
    * - :class:`ExecutionStatus`
      - Describes the final status of a scenario or campaign execution.
      - :class:`._executionstatus.ExecutionStatus`
    """
    from ._executionstatus import ExecutionStatus as ExecutionStatus
    __all__.append("ExecutionStatus")

if __pkg_def:
    __doc__ += """
    * - :class:`ScenarioExecution`
      -
      - :class:`._scenarioexecution.ScenarioExecution`
    """
    from ._scenarioexecution import ScenarioExecution as ScenarioExecution
    __all__.append("ScenarioExecution")

if __pkg_def:
    __doc__ += """
    * - :class:`StepExecution`
      -
      - :class:`._stepexecution.StepExecution`
    """
    from ._stepexecution import StepExecution as StepExecution
    __all__.append("StepExecution")

if __pkg_def:
    __doc__ += """
    * - :class:`ActionResultExecution`
      -
      - :class:`._actionresultexecution.ActionResultExecution`
    """
    from ._actionresultexecution import ActionResultExecution as ActionResultExecution
    __all__.append("ActionResultExecution")

if __pkg_def:
    __doc__ += """
    * - :class:`CampaignExecution`
      -
      - :class:`._campaignexecution.CampaignExecution`
    """
    from ._campaignexecution import CampaignExecution as CampaignExecution
    __all__.append("CampaignExecution")

if __pkg_def:
    __doc__ += """
    * - :class:`TestSuiteExecution`
      -
      - :class:`._campaignexecution.TestSuiteExecution`
    """
    from ._campaignexecution import TestSuiteExecution as TestSuiteExecution
    __all__.append("TestSuiteExecution")

if __pkg_def:
    __doc__ += """
    * - :class:`TestCaseExecution`
      -
      - :class:`._campaignexecution.TestCaseExecution`
    """
    from ._campaignexecution import TestCaseExecution as TestCaseExecution
    __all__.append("TestCaseExecution")

__doc__ += __export_table_end

__doc__ += """
:ref:`Error management <errors>`:
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :class:`TestError`
      - Base class that describes an error that occurred during the tests.
      - :class:`._testerrors.TestError`
    """
    from ._testerrors import TestError as TestError
    __all__.append("TestError")

if __pkg_def:
    __doc__ += """
    * - :class:`ExceptionError`
      - Subclass of :class:`TestError` that describes an error due to an exception that occurred during the tests.
      - :class:`._testerrors.ExceptionError`
    """
    from ._testerrors import ExceptionError as ExceptionError
    __all__.append("ExceptionError")

if __pkg_def:
    __doc__ += """
    * - :class:`KnownIssue`
      - Subclass of :class:`TestError` that describes a known issue.
      - :class:`._knownissues.KnownIssue`
    """
    from ._knownissues import KnownIssue as KnownIssue
    __all__.append("KnownIssue")

__doc__ += __export_table_end

__doc__ += """
Statistics:
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :class:`TimeStats`
      - Describes execution time statistics.
      - :class:`._stats.TimeStats`
    """
    from ._stats import TimeStats as TimeStats
    __all__.append("TimeStats")

if __pkg_def:
    __doc__ += """
    * - :class:`ExecTotalStats`
      - Describes count statistics: number of items executed, out of the total number of items.
      - :class:`._stats.ExecTotalStats`
    """
    from ._stats import ExecTotalStats as ExecTotalStats
    __all__.append("ExecTotalStats")

__doc__ += __export_table_end


__doc__ += """
Reports (advanced)
==================

The following objects give you the opportunity to read and write :ref:`scenario and campaign reports <reports>`.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :attr:`report`
      - Scenario report manager.
      - :class:`._scenarioreport.ScenarioReport`
    """
    from ._scenarioreport import SCENARIO_REPORT as report  # noqa  ## Constant variable imported as non-constant
    __all__.append("report")

if __pkg_def:
    __doc__ += """
    * - :attr:`campaign_report`
      - Campaign report manager.
      - :class:`._campaignreport.CampaignReport`
    """
    from ._campaignreport import CAMPAIGN_REPORT as campaign_report  # noqa  ## Constant variable imported as non-constant
    __all__.append("campaign_report")

__doc__ += __export_table_end


__doc__ += """
Miscellaneous
=============

The `scenario` framework also exposes a couple of useful classes and types that may be used.
"""

__doc__ += __export_table_start

if __pkg_def:
    __doc__ += """
    * - :class:`Path`
      - ``pathlib.Path`` augmentation:

        - absolute / relative paths disambiguation,
        - pretty displays inside a project root path.

      - :class:`._path.Path`
    """
    from ._path import Path as Path
    __all__.append("Path")
if typing.TYPE_CHECKING:
    __doc__ += """
    * - :class:`AnyPathType`
      - Any kind of path, :class:`Path` included.
      - :class:`._path.AnyPathType`
    """
    from ._path import AnyPathType as AnyPathType
    __all__.append("AnyPathType")

if __pkg_def:
    __doc__ += """
    * - :class:`SubProcess`
      - Eases the way to prepare a sub-process, execute it, and retrieve its results.
      - :class:`._subprocess.SubProcess`
    """
    from ._subprocess import SubProcess as SubProcess
    __all__.append("SubProcess")
if typing.TYPE_CHECKING:
    __doc__ += """
    * - :class:`VarSubProcessType`
      - Variable subprocess type, :class:`SubProcess` and subclasses.
      - :class:`._subprocess.VarSubProcessType`
    """
    from ._subprocess import VarSubProcessType as VarSubProcessType
    __all__.append("VarSubProcessType")

if __pkg_def:
    __doc__ += """
    * - :class:`CodeLocation`
      -
      - :class:`._locations.CodeLocation`
    """
    from ._locations import CodeLocation as CodeLocation
    __all__.append("CodeLocation")

if __pkg_def:
    __doc__ += """
    * - :mod:`datetime`
      - Date/time utils.
      - :mod:`._datetimeutils`
    """
    from . import _datetimeutils as datetime
    __all__.append("datetime")

if __pkg_def:
    __doc__ += """
    * - :mod:`timezone`
      - Timezone utils.
      - :mod:`._timezoneutils`
    """
    from . import _timezoneutils as timezone
    __all__.append("timezone")

if __pkg_def:
    __doc__ += """
    * - :mod:`enum`
      - Enum utils.
      - :mod:`._enumutils`
    """
    from . import _enumutils as enum
    __all__.append("enum")

__doc__ += __export_table_end
