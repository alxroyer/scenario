.. Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..     http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.


The following table describes the `scenario` configurable keys & values.

.. tip::

    Use the :py:class:`scenario.ConfigKey` shortcut to the internal :py:class:`scenario._scenarioconfig.ScenarioConfig.Key` enum
    from `scenario` user code.

.. list-table:: Scenario configurable keys and values
    :widths: auto
    :header-rows: 1
    :stub-columns: 0

    * - Key
      -
      - Type
      - Description
      - Default

    * - `Time & logging`
      -
      -
      -
      -

    * - .. _config-db.scenario.timezone:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.TIMEZONE`
      - ``scenario.timezone``
      - String
      - Timezone specification.

        Possible values:
        'UTC', 'Z',
        or numerical forms like '+01:00', '-05:00'.

        More options :ref:`when pytz is installed <install>`:
        'CET', 'US/Pacific', 'Japan', ...

        Execute the following Python code for the complete list:

        .. code-block:: python

            import pytz
            print("\n".join(pytz.all_timezones))

      - Not set, i.e. use of the local timezone

    * - .. _config-db.scenario.log_datetime:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.LOG_DATETIME`
      - ``scenario.log_datetime``
      - Boolean
      - Should the log lines include a timestamp?
      - Enabled

    * - .. _config-db.scenario.log_console:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.LOG_CONSOLE`
      - ``scenario.log_console``
      - Boolean
      - Should the log lines be displayed in the console?
      - Enabled

    * - .. _config-db.scenario.log_color:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.LOG_COLOR_ENABLED`
      - ``scenario.log_color``
      - Boolean
      - Should the log lines be colored?
      - Enabled

    * - .. _config-db.scenario.log_level_color:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.LOG_COLOR`
      - ``scenario.log_%(level)_color``,
        ``%(level)`` being one of (``error``, ``warning``, ``info``, ``debug``)
      - Integer
      - Console color code per log level.
        See :py:class:`scenario._consoleutils.Console.Color` for a list useful color codes.
      - scenario.log_error_color: red(91),
        scenario.log_warning_color: yellow(33),
        scenario.log_info_color: white(1),
        scenario.log_debug_color: dark grey(2)

    * - .. _config-db.scenario.log_file:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.LOG_FILE`
      - ``scenario.log_file``
      - Absolute path string
      - Should the log lines be written in a log file?
      - Not set, i.e. no file logging

    * - .. _config-db.scenario.debug_classes:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.DEBUG_CLASSES`
      - ``scenario.debug_classes``
      - List of strings (or comma-separated string)
      - Which debug classes to display?
      - Not set

    * - `Requirement management`
      -
      -
      -
      -

    * - .. _config-db.scenario.req_db_files:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.REQ_DB_FILES`
      - ``scenario.req_db_files``
      - List of absolute path strings (or comma-separated string)
      - List of requirement files to load.

        Absolute paths, or relative paths to the configuration file they are defined into.

        Applicable when running tests and campaigns.
      - Not set

    * - .. _config-db.scenario.expect_step_req_refinement:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.EXPECT_STEP_REQ_REFINEMENT`
      - ``scenario.expect_step_req_refinement``
      - Boolean
      - Should the scenario requirement coverage be refined on steps?
      - Not set

    * - `Test & campaign execution`
      -
      -
      -
      -

    * - .. _config-db.scenario.expected_scenario_attributes:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.EXPECTED_SCENARIO_ATTRIBUTES`
      - ``scenario.expected_scenario_attributes``
      - List of strings (or comma-separated string)
      - Expected scenario attributes.
      - Not set

    * - .. _config-db.scenario.continue_on_error:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.CONTINUE_ON_ERROR`
      - ``scenario.continue_on_error``
      - Boolean
      - Should the scenarios continue on error?
        If set to ``True``, an error ends the current step, but following steps are still executed.
        The same behaviour may also be activated scenario by scenario
        by using the :py:meth:`scenario._scenariodefinition.ScenarioDefinition.continueonerror()` method.
      - Disabled

    * - .. _config-db.scenario.delay_between_steps:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.DELAY_BETWEEN_STEPS`
      - ``scenario.delay_between_steps``
      - Float (in seconds)
      - Should we wait between two step executions?
      - 0.001 seconds

    * - .. _config-db.scenario.runner_script_path:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.RUNNER_SCRIPT_PATH`
      - ``scenario.runner_script_path``
      - Absolute path string
      - Path of the scenario runner script.
        Useful when executing campaigns: may be used to make your own :ref:`launcher script path <launcher>` be called.
      - 'bin/run-test.py' provided with the `scenario` framework

    * - .. _config-db.scenario.test_suite_files:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.TEST_SUITE_FILES`
      - ``scenario.test_suite_files``
      - List of absolute path strings (or comma-separated string)
      - Default test suite files.
        Useful when executing campaigns or requirement management.
      - Not set

    * - .. _config-db.scenario.scenario_timeout:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.SCENARIO_TIMEOUT`
      - ``scenario.scenario_timeout``
      - Float (in seconds)
      - Maximum time for a scenario execution. Useful when executing campaigns.
      - 600.0 seconds, i.e. 10 minutes

    * - `Results & reports`
      -
      -
      -
      -

    * - .. _config-db.scenario.results_extra_info:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.RESULTS_EXTRA_INFO`
      - ``scenario.results_extra_info``
      - List of strings (or comma-separated string)
      - Scenario attributes to display for extra info when displaying scenario results,
        after a campaign execution, or when executing several tests in a single command line.
      - Not set

    * - .. _config-db.scenario.scenario_report_suffix:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.SCENARIO_REPORT_SUFFIX`
      - ``scenario.scenario_report_suffix``
      - String
      - Scenario report suffix.

        Used when executing campaigns.
      - '.json'

    * - .. _config-db.scenario.campaign_report_filename:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.CAMPAIGN_REPORT_FILENAME`
      - ``scenario.campaign_report_filename``
      - String
      - Campaign report file name used when reading / writing campaign results.
      - 'campaign.xml'

    * - .. _config-db.scenario.req_db_filename:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.REQ_DB_FILENAME`
      - ``scenario.req_db_filename``
      - String
      - Requirement database file name used when reading / writing campaign results.
      - 'req-db.json'

    * - .. _config-db.scenario.downstream_traceability_filename:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.DOWNSTREAM_TRACEABILITY_FILENAME`
      - ``scenario.downstream_traceability_filename``
      - String
      - Downstream traceability report file name used when reading / writing campaign results.
      - 'req-downstream-traceability.json'

    * - .. _config-db.scenario.upstream_traceability_filename:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.UPSTREAM_TRACEABILITY_FILENAME`
      - ``scenario.upstream_traceability_filename``
      - String
      - Upstream traceability report file name used when reading / writing campaign results.
      - 'req-upstream-traceability.json'

    * - `Known issues and issue levels`
      -
      -
      -
      -

    * - .. _config-db.scenario.issue_levels:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.ISSUE_LEVEL_NAMES`
      - ``scenario.issue_levels``
      - ``{str: int}`` dictionary
      - Dictionary of names associated with issue level integer values.

        Example:

        .. code-block:: YAML

            scenario:
              issue_levels:
                SUT: 40
                TEST: 30
                CONTEXT: 20
                PLANNED: 10
      - Not set

    * - .. _config-db.scenario.issue_level_error:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.ISSUE_LEVEL_ERROR`
      - ``scenario.issue_level_error``
      - String or integer
      - Issue level from and above which known issues should be considered as errors.

        May be set directly as an integer value, or an issue level name if defined (see :ref:`scenario.issue_levels <config-db.scenario.issue_levels>`).
      - Not set

    * - .. _config-db.scenario.issue_level_ignored:

        :py:attr:`scenario._scenarioconfig.ScenarioConfig.Key.ISSUE_LEVEL_IGNORED`
      - ``scenario.issue_level_ignored``
      - String or integer
      - Issue level from and under which known issues should be ignored.

        May be set directly as an integer value, or an issue level name if defined (see :ref:`scenario.issue_levels <config-db.scenario.issue_levels>`).
      - Not set

    * - `User Interface`
      -
      -
      -
      -

    * - .. _config-db.scenario.ui_main_path:

        :py:attr:`scenario.ui._configdb.UIConfig.Key.MAIN_PATH`
      - ``scenario.ui.main_path``
      - Absolute path string
      - Main path for `scenario.ui` execution.
      - 'ui/' directory provided with the `scenario` framework

    * - .. _config-db.scenario.ui_css_url:

        :py:attr:`scenario.ui._configdb.UIConfig.Key.CSS_URL`
      - ``scenario.ui.css_url``
      - String
      - Main `scenario.ui` CSS URL.
      - 'css/ui.css'

    * - .. _config-db.scenario.ui_js_url:

        :py:attr:`scenario.ui._configdb.UIConfig.Key.JS_URL`
      - ``scenario.ui.js_url``
      - String
      - Main `scenario.ui` Javascript URL.
      - 'js/ui.js'
