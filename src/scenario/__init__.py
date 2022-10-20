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
# That's the reason why we manually document the exported symbols with explicit ResStructuredText as aliases to the inner classes,
# which lets us define documentation sections by the way.

"""
:mod:`scenario` package definition.
"""

# Inspired from https://packaging.python.org/guides/packaging-namespace-packages/#creating-a-namespace-package
# Define this package as a namespace, so that it can be extended later on (with tools, tests, ...).
# In as much as this code is python 2/3 compatible, we use *pkgutil-style namespace packages*.
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

# Make system imports after the namespace definition above.
import typing


__doc__ += """
Base classes
============

Classes to inherit from in order to describe test scenarios and libraries.
"""

__doc__ += """
.. py:attribute:: Scenario

    Alias of :class:`.scenariodefinition.ScenarioDefinition`.

    Base class to inherit from in order to define a test scenario.
"""
from .scenariodefinition import ScenarioDefinition as Scenario  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: Step

    Alias of :class:`.stepdefinition.StepDefinition`.

    Base class to inherit from in order to define a test step.
"""
from .stepdefinition import StepDefinition as Step  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: ActionResult

    Alias of :class:`.actionresultdefinition.ActionResultDefinition`.
"""
from .actionresultdefinition import ActionResultDefinition as ActionResult  # noqa: E402  ## Module level import not at top of file


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
from .assertions import Assertions  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: assertionhelpers

    Alias of :mod:`.assertionhelpers`.

    Helper functions and types when you want to write your own assertion routines.
"""
from . import assertionhelpers  # noqa: E402  ## Module level import not at top of file


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
from .logger import Logger  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: logging

    Main logger instance.
"""
# noinspection PyPep8Naming
from .loggermain import MAIN_LOGGER as logging  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: Console

    Alias of :class:`.console.Console`.

    Console colors.
"""
from .console import Console  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: LogExtraData

    Alias of :class:`.logextradata.LogExtraData`.

    Logging extra data management.
"""
from .logextradata import LogExtraData  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: debug

    Alias of :mod:`.debugutils`.

    Helper functions and types for debugging.
"""
from . import debugutils as debug  # noqa: E402  ## Module level import not at top of file


__doc__ += """
Configuration
=============

Configuration management.
"""

__doc__ += """
.. py:attribute:: conf

    Configuration manager instance.
"""
# noinspection PyPep8Naming
from .configdb import CONFIG_DB as conf  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: ConfigNode

    Alias of :class:`.confignode.ConfigNode`.
"""
from .confignode import ConfigNode  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: ConfigKey

    Alias of :class:`.scenarioconfig.ScenarioConfig.Key`.

    :mod:`scenario` configuration keys.
"""
from .scenarioconfig import ScenarioConfigKey as ConfigKey  # noqa: E402  ## Module level import not at top of file


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
# noinspection PyPep8Naming
from .scenariorunner import SCENARIO_RUNNER as runner  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: campaign_runner

    Campaign runner instance.

    Call from your own campaign launcher script with:

    .. code-block:: python

        scenario.campaign_runner.main()
"""
# noinspection PyPep8Naming
from .campaignrunner import CAMPAIGN_RUNNER as campaign_runner  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: Args

    Alias of :class:`.args.Args`.

    Base class for :class:`ScenarioArgs` and :class:`CampaignArgs`.
"""
from .args import Args  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: ScenarioArgs

    Alias of :class:`.scenarioargs.ScenarioArgs`.

    Inherit from this class in order to extend :class:`.scenariorunner.ScenarioRunner` arguments with your own launcher script ones.
"""
from .scenarioargs import ScenarioArgs  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: CampaignArgs

    Alias of :class:`.campaignargs.CampaignArgs`.

    Inherit from this class in order to extend :class:`.campaignrunner.CampaignRunner` arguments with your own launcher script ones.
"""
from .campaignargs import CampaignArgs  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: ErrorCode

    Alias of :class:`.errcodes.ErrorCode`.

    Error codes returned by the :meth:`main()` methods of :class:`.scenariorunner.ScenarioRunner` and :class:`.campaignrunner.CampaignRunner`.
"""
from .errcodes import ErrorCode  # noqa: E402  ## Module level import not at top of file


__doc__ += """
Handlers (advanced)
===================

Add reactive code.
"""

__doc__ += """
.. py:attribute:: handlers

    Handler manager instance.
"""
# noinspection PyPep8Naming
from .handlers import HANDLERS as handlers  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: Event

    Alias of :class:`.scenarioevents.ScenarioEvent`.
"""
from .scenarioevents import ScenarioEvent as Event  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: EventData

    Alias of :class:`.scenarioevents.ScenarioEventData`.
"""
from .scenarioevents import ScenarioEventData as EventData  # noqa: E402  ## Module level import not at top of file


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
from .executionstatus import ExecutionStatus  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: ScenarioExecution

    Alias of :class:`.scenarioexecution.ScenarioExecution`.
"""
from .scenarioexecution import ScenarioExecution  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: StepExecution

    Alias of :class:`.stepexecution.StepExecution`.
"""
from .stepexecution import StepExecution  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: ActionResultExecution

    Alias of :class:`.actionresultexecution.ActionResultExecution`.
"""
from .actionresultexecution import ActionResultExecution  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py::attribute:: CampaignExecution

    Alias of :class:`.campaignexecutions.CampaignExecution`.
"""
from .campaignexecution import CampaignExecution  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py::attribute:: TestSuiteExecution

    Alias of :class:`.campaignexecutions.TestSuiteExecution`.
"""
from .campaignexecution import TestSuiteExecution  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py::attribute:: TestCaseExecution

    Alias of :class:`.campaignexecutions.TestCaseExecution`.
"""
from .campaignexecution import TestCaseExecution  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: TestError

    Alias of :class:`.testerrors.TestError`.

    Describes an error that occurred during the tests.
"""
from .testerrors import TestError  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: ExceptionError

    Alias of :class:`.testerrors.ExceptionError`.

    Describes an error due to an exception that occurred during the tests.
"""
from .testerrors import ExceptionError  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: KnownIssue

    Alias of :class:`.testerrors.KnownIssue`.

    Describes an error due to an exception that occurred during the tests.
"""
from .testerrors import KnownIssue  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: TimeStats

    Alias of :class:`.stats.TimeStats`.

    Describes execution time statistics.
"""
from .stats import TimeStats  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: ExecTotalStats

    Alias of :class:`.stats.ExecTotalStats`.

    Describes count statistics: number of items executed, out of the total number of items.
"""
from .stats import ExecTotalStats  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: stack

    Sscenario stack instance.
"""
# noinspection PyPep8Naming
from .scenariostack import SCENARIO_STACK as stack  # noqa: E402  ## Module level import not at top of file


__doc__ += """
Reports (advanced)
==================

The following objects give you the opportunity to read and write scenario and campaign reports.
"""

__doc__ += """
.. py:attribute:: report

    Scenario report manager.
"""
# noinspection PyPep8Naming
from .scenarioreport import SCENARIO_REPORT as report  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: campaign_report

    Campaign report manager.
"""
# noinspection PyPep8Naming
from .campaignreport import CAMPAIGN_REPORT as campaign_report  # noqa: E402  ## Module level import not at top of file


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
from .path import Path  # noqa: E402  ## Module level import not at top of file
if typing.TYPE_CHECKING:
    from .path import AnyPathType

__doc__ += """
.. py:attribute:: SubProcess

    Alias of :class:`.subprocess.SubProcess`.

    Eases the way to prepare a sub-process, execute it, and then retrieve its results.


.. py:attribute:: VarSubProcessType

    Alias of :class:`.subprocess.VarSubProcessType`.
"""
from .subprocess import SubProcess  # noqa: E402  ## Module level import not at top of file
if typing.TYPE_CHECKING:
    from .subprocess import VarSubProcessType

__doc__ += """
.. py:attribute:: CodeLocation

    Alias of :class:`.locations.CodeLocation`.
"""
from .locations import CodeLocation  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: datetime

    Alias of :mod:`.datetimeutils`.

    Date/time utils.
"""
from . import datetimeutils as datetime  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: tz

    Alias of :mod:`.timezoneutils`.

    Timezone utils.
"""
from . import timezoneutils as timezone  # noqa: E402  ## Module level import not at top of file

__doc__ += """
.. py:attribute:: enum

    Alias of :mod:`.enumutils`.

    Enumerate utils.
"""
from . import enumutils as enum  # noqa: E402  ## Module level import not at top of file
