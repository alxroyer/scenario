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

# Inspired from https://packaging.python.org/guides/packaging-namespace-packages/#creating-a-namespace-package
# Define this package as a namespace, so that it can be extended later on (with tools, tests, ...).
# In as much as this code is python 2/3 compatible, we use *pkgutil-style namespace packages*.
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)  # noqa  ## Name '__path__' can be undefined

# Make system imports after the namespace definition above.
import typing


# Used to avoid PEP8 E402 warnings: "Module level import not at top of file".
# Named with double leading underscores in order to avoid 'mkdoc.py' list it as an undocumented attribute.
__pkg_def = True  # type: bool

# A couple of symbols are exported by using an intermediate private symbol.
# For instance, if we declare `logging` as following:
# ```python
# from .loggermain import MAIN_LOGGER as logging
# ```
# mypy fails with '"Module scenario" does not explicitly export attribute "logging"  [attr-defined]' errors.
# Mypy seems not to support reexports with renamings.
# Possibly something to do with [PEP 0848](https://peps.python.org/pep-0484/#stub-files) reexport rules for stub files...


__doc__ += """
Package information
===================
"""

__doc__ += """
.. py:attribute:: info

    Alias of :attr:`.pkginfo.PKG_INFO`.

    Gives the package information: version, ...
"""
if __pkg_def:
    from .pkginfo import PKG_INFO as _PKG_INFO
    info = _PKG_INFO


__doc__ += """
Base classes
============

Classes to inherit from in order to describe test scenarios and libraries.
"""

__doc__ += """
.. py:attribute:: Scenario

    Alias of :class:`.scenariodefinition.ScenarioDefinition`.

    Base class to inherit from in order to define a test scenario.

.. py:attribute:: ScenarioDefinition

    Full class name of :class:`Scenario`.
"""
if __pkg_def:
    from .scenariodefinition import ScenarioDefinition as ScenarioDefinition
    Scenario = ScenarioDefinition

__doc__ += """
.. py:attribute:: Step

    Alias of :class:`.stepdefinition.StepDefinition`.

    Base class to inherit from in order to define a test step.

.. py:attribute:: StepDefinition

    Full class name of :class:`Step`.
"""
if __pkg_def:
    from .stepdefinition import StepDefinition as StepDefinition
    Step = StepDefinition

__doc__ += """
.. py:attribute:: ActionResult

    Alias of :class:`.actionresultdefinition.ActionResultDefinition`.

.. py:attribute:: ActionResultDefinition

    Full class name of :class:`ActionResult`.
"""
if __pkg_def:
    from .actionresultdefinition import ActionResultDefinition as ActionResultDefinition
    ActionResult = ActionResultDefinition


__doc__ += """
Step sections
=============

Classes that can be used to define step sections.
"""

__doc__ += """
.. py:attribute:: StepSectionDescription

    Alias of :class:`.stepsection.StepSectionDescription`.

    Step class that holds a description for a section of steps.
    Automatically instanciated by :meth:`.scenariodefinition.ScenarioDefinition.section()`.
"""
if __pkg_def:
    from .stepsection import StepSectionDescription as StepSectionDescription

__doc__ += """
.. py:attribute:: StepSectionBegin

    Alias of :class:`.stepsection.StepSectionBegin`.

    Step class to inherit from, then add in a scenario, in order to define the beginning of a step section.
"""
if __pkg_def:
    from .stepsection import StepSectionBegin as StepSectionBegin

__doc__ += """
.. py:attribute:: StepSectionEnd

    Alias of :class:`.stepsection.StepSectionEnd`.

    Type of the :attr:`.stepsection.StepSectionBegin.end` step to add at the end of a step section.
"""
if __pkg_def:
    from .stepsection import StepSectionEnd as StepSectionEnd


__doc__ += """
Assertions
==========

Make verifications on data.
"""

__doc__ += """
.. py:attribute:: Assertions

    Alias of :class:`.assertions.Assertions`.

    Library of static assertion methods.

    Can be sub-classes.
    :class:`Scenario` and :class:`Step` inherit from this class.
"""
if __pkg_def:
    from .assertions import Assertions as Assertions

__doc__ += """
.. py:attribute:: assertionhelpers

    Alias of :mod:`.assertionhelpers`.

    Helper functions and types when you want to write your own assertion routines.
"""
if __pkg_def:
    from . import assertionhelpers as assertionhelpers


__doc__ += """
Logging
=======

Logging management.
"""

__doc__ += """
.. py:attribute:: Logger

    Alias of :class:`.logger.Logger`.

    Object with logging capabilities.

    :class:`Scenario` and :class:`Step` inherit from this class.
"""
if __pkg_def:
    from .logger import Logger as Logger

__doc__ += """
.. py:attribute:: logging

    Main logger instance.
"""
if __pkg_def:
    from .loggermain import MAIN_LOGGER as _MAIN_LOGGER
    logging = _MAIN_LOGGER

__doc__ += """
.. py:attribute:: Console

    Alias of :class:`.console.Console`.

    Console colors.
"""
if __pkg_def:
    from .console import Console as Console

__doc__ += """
.. py:attribute:: LogExtraData

    Alias of :class:`.logextradata.LogExtraData`.

    Logging extra data management.
"""
if __pkg_def:
    from .logextradata import LogExtraData as LogExtraData

__doc__ += """
.. py:attribute:: debug

    Alias of :mod:`.debugutils`.

    Helper functions and types for debugging.
"""
if __pkg_def:
    from . import debugutils as debug


__doc__ += """
Configuration
=============

Configuration management.
"""

__doc__ += """
.. py:attribute:: conf

    Configuration manager instance.
"""
if __pkg_def:
    from .configdb import CONFIG_DB as _CONFIG_DB
    conf = _CONFIG_DB

__doc__ += """
.. py:attribute:: ConfigNode

    Alias of :class:`.confignode.ConfigNode`.
"""
if __pkg_def:
    from .confignode import ConfigNode as ConfigNode

__doc__ += """
.. py:attribute:: ConfigKey

    Alias of :class:`.scenarioconfig.ScenarioConfig.Key`.

    `scenario` configuration keys.
"""
if __pkg_def:
    from .scenarioconfig import ScenarioConfig as _ScenarioConfig
    ConfigKey = _ScenarioConfig.Key


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
"""
if __pkg_def:
    from .scenariorunner import SCENARIO_RUNNER as _SCENARIO_RUNNER
    runner = _SCENARIO_RUNNER

__doc__ += """
.. py:attribute:: campaign_runner

    Campaign runner instance.

    Call from your own campaign launcher script with:

    .. code-block:: python

        scenario.campaign_runner.main()
"""
if __pkg_def:
    from .campaignrunner import CAMPAIGN_RUNNER as _CAMPAIGN_RUNNER
    campaign_runner = _CAMPAIGN_RUNNER

__doc__ += """
.. py:attribute:: Args

    Alias of :class:`.args.Args`.

    Base class for :class:`ScenarioArgs` and :class:`CampaignArgs`.
"""
if __pkg_def:
    from .args import Args as Args

__doc__ += """
.. py:attribute:: ScenarioArgs

    Alias of :class:`.scenarioargs.ScenarioArgs`.

    Inherit from this class in order to extend :class:`.scenariorunner.ScenarioRunner` arguments with your own launcher script ones.
"""
if __pkg_def:
    from .scenarioargs import ScenarioArgs as ScenarioArgs

__doc__ += """
.. py:attribute:: CampaignArgs

    Alias of :class:`.campaignargs.CampaignArgs`.

    Inherit from this class in order to extend :class:`.campaignrunner.CampaignRunner` arguments with your own launcher script ones.
"""
if __pkg_def:
    from .campaignargs import CampaignArgs as CampaignArgs

__doc__ += """
.. py:attribute:: ErrorCode

    Alias of :class:`.errcodes.ErrorCode`.

    Error codes returned by the :meth:`main()` methods of :class:`.scenariorunner.ScenarioRunner` and :class:`.campaignrunner.CampaignRunner`.
"""
if __pkg_def:
    from .errcodes import ErrorCode as ErrorCode


__doc__ += """
Handlers (advanced)
===================

Add reactive code.
"""

__doc__ += """
.. py:attribute:: handlers

    Handler manager instance.
"""
if __pkg_def:
    from .handlers import HANDLERS as _HANDLERS
    handlers = _HANDLERS

__doc__ += """
.. py:attribute:: Event

    Alias of :class:`.scenarioevents.ScenarioEvent`.
"""
if __pkg_def:
    from .scenarioevents import ScenarioEvent as _ScenarioEvent
    Event = _ScenarioEvent

__doc__ += """
.. py:attribute:: EventData

    Alias of :class:`.scenarioevents.ScenarioEventData`.
"""
if __pkg_def:
    from .scenarioevents import ScenarioEventData as _ScenarioEventData
    EventData = _ScenarioEventData


__doc__ += """
Execution result classes (advanced)
===================================

Sometimes, you may need to access information about the test execution itself.
"""

__doc__ += """
.. py:attribute:: ExecutionStatus

    Alias of :class:`.executionstatus.ExecutionStatus`.

    Describes the final status of a scenario or campaign execution.
"""
if __pkg_def:
    from .executionstatus import ExecutionStatus as ExecutionStatus

__doc__ += """
.. py:attribute:: ScenarioExecution

    Alias of :class:`.scenarioexecution.ScenarioExecution`.
"""
if __pkg_def:
    from .scenarioexecution import ScenarioExecution as ScenarioExecution

__doc__ += """
.. py:attribute:: StepExecution

    Alias of :class:`.stepexecution.StepExecution`.
"""
if __pkg_def:
    from .stepexecution import StepExecution as StepExecution

__doc__ += """
.. py:attribute:: ActionResultExecution

    Alias of :class:`.actionresultexecution.ActionResultExecution`.
"""
if __pkg_def:
    from .actionresultexecution import ActionResultExecution as ActionResultExecution

__doc__ += """
.. py::attribute:: CampaignExecution

    Alias of :class:`.campaignexecutions.CampaignExecution`.
"""
if __pkg_def:
    from .campaignexecution import CampaignExecution as CampaignExecution

__doc__ += """
.. py::attribute:: TestSuiteExecution

    Alias of :class:`.campaignexecutions.TestSuiteExecution`.
"""
if __pkg_def:
    from .campaignexecution import TestSuiteExecution as TestSuiteExecution

__doc__ += """
.. py::attribute:: TestCaseExecution

    Alias of :class:`.campaignexecutions.TestCaseExecution`.
"""
if __pkg_def:
    from .campaignexecution import TestCaseExecution as TestCaseExecution

__doc__ += """
.. py:attribute:: TestError

    Alias of :class:`.testerrors.TestError`.

    Describes an error that occurred during the tests.
"""
if __pkg_def:
    from .testerrors import TestError as TestError

__doc__ += """
.. py:attribute:: ExceptionError

    Alias of :class:`.testerrors.ExceptionError`.

    Describes an error due to an exception that occurred during the tests.
"""
if __pkg_def:
    from .testerrors import ExceptionError as ExceptionError

__doc__ += """
.. py:attribute:: KnownIssue

    Alias of :class:`.knownissues.KnownIssue`.

    Describes an error due to an exception that occurred during the tests.
"""
if __pkg_def:
    from .knownissues import KnownIssue as KnownIssue

__doc__ += """
.. py:attribute:: IssueLevel

    Alias of :class:`.issuelevels.IssueLevel`.

    Provides methods to define named issue levels.

.. py:attribute:: AnyIssueLevelType

    Alias of :class:`.issuelevels.AnyIssueLevelType`.
"""
if __pkg_def:
    from .issuelevels import IssueLevel as IssueLevel
if typing.TYPE_CHECKING:
    from .issuelevels import AnyIssueLevelType as AnyIssueLevelType

__doc__ += """
.. py:attribute:: TimeStats

    Alias of :class:`.stats.TimeStats`.

    Describes execution time statistics.
"""
if __pkg_def:
    from .stats import TimeStats as TimeStats

__doc__ += """
.. py:attribute:: ExecTotalStats

    Alias of :class:`.stats.ExecTotalStats`.

    Describes count statistics: number of items executed, out of the total number of items.
"""
if __pkg_def:
    from .stats import ExecTotalStats as ExecTotalStats

__doc__ += """
.. py:attribute:: stack

    Scenario stack instance.
"""
if __pkg_def:
    from .scenariostack import SCENARIO_STACK as _SCENARIO_STACK
    stack = _SCENARIO_STACK


__doc__ += """
Reports (advanced)
==================

The following objects give you the opportunity to read and write scenario and campaign reports.
"""

__doc__ += """
.. py:attribute:: report

    Scenario report manager.
"""
if __pkg_def:
    from .scenarioreport import SCENARIO_REPORT as _SCENARIO_REPORT
    report = _SCENARIO_REPORT

__doc__ += """
.. py:attribute:: campaign_report

    Campaign report manager.
"""
if __pkg_def:
    from .campaignreport import CAMPAIGN_REPORT as _CAMPAIGN_REPORT
    campaign_report = _CAMPAIGN_REPORT


__doc__ += """
Miscellaneous
=============
"""

__doc__ += """
.. py:attribute:: Path

    Alias of :class:`.path.Path`.


.. py:attribute:: AnyPathType

    Alias of :class:`.path.AnyPathType`.
"""
if __pkg_def:
    from .path import Path as Path
if typing.TYPE_CHECKING:
    from .path import AnyPathType as AnyPathType

__doc__ += """
.. py:attribute:: SubProcess

    Alias of :class:`.subprocess.SubProcess`.

    Eases the way to prepare a sub-process, execute it, and then retrieve its results.


.. py:attribute:: VarSubProcessType

    Alias of :class:`.subprocess.VarSubProcessType`.
"""
if __pkg_def:
    from .subprocess import SubProcess as SubProcess
if typing.TYPE_CHECKING:
    from .subprocess import VarSubProcessType as VarSubProcessType

__doc__ += """
.. py:attribute:: CodeLocation

    Alias of :class:`.locations.CodeLocation`.
"""
if __pkg_def:
    from .locations import CodeLocation as CodeLocation

__doc__ += """
.. py:attribute:: datetime

    Alias of :mod:`.datetimeutils`.

    Date/time utils.
"""
if __pkg_def:
    from . import datetimeutils as datetime

__doc__ += """
.. py:attribute:: tz

    Alias of :mod:`.timezoneutils`.

    Timezone utils.
"""
if __pkg_def:
    from . import timezoneutils as timezone

__doc__ += """
.. py:attribute:: enum

    Alias of :mod:`.enumutils`.

    Enum utils.
"""
if __pkg_def:
    from . import enumutils as enum
