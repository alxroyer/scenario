#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo test launcher.
"""

import logging
import pathlib
import sys

# Path management.
MAIN_PATH = pathlib.Path(__file__).parents[1]
sys.path.append(str(MAIN_PATH / "src"))

import scenario  # noqa: E402


class DemoArgs(scenario.ScenarioArgs):
    def __init__(self):
        scenario.ScenarioArgs.__init__(
            self,
            # Define scenario paths as optional.
            def_scenario_paths_arg=False,
        )

        self.setdescription("Demo test launcher.")

        # Add a demo argument group.
        self._demo_group = self._arg_parser.add_argument_group("Demo arguments")

        self._demo_group.add_argument(
            "--welcome", metavar="NAME",
            dest="welcome_name", action="store", type=str, default=None,
            help="User name.",
        )

        # Extend configuration options with a `--show-configs` option.
        self._config_group.add_argument(
            "--show-configs",
            dest="show_config_db", action="store_true", default=False,
            help="Show the configuration values with their origin, then stop.",
        )

        # Define scenario paths as optional.
        self._defscenariopathsarg(
            nargs="*",
            help="Scenario script(s) to execute. Mandatory unless the --show-configs option is used",
        )

    def _checkargs(self):
        if not super()._checkargs():
            return False

        if self._args.welcome_name is not None:
            self._args.welcome_name = self._args.welcome_name.strip()
            if not self._args.welcome_name:
                scenario.logging.error(f"Wrong name {self._args.welcome_name!r}")
                return False

        if (not self.scenario_paths) and (not self.show_config_db):
            scenario.logging.error("Use either the --show-configs option, or give scenario paths")
            return False

        return True

    @property
    def welcome_message(self):  # type: (...) -> str
        if self._args.welcome_name:
            return f"Hello {self._args.welcome_name}!"
        else:
            return "Hello you!"

    @property
    def bye_message(self):  # type: (...) -> str
        if self._args.welcome_name:
            return f"Bye {self._args.welcome_name}!"
        else:
            return "Bye!"

    @property
    def show_config_db(self):  # type: (...) -> bool
        return self._args.show_config_db


if __name__ == "__main__":
    # Command line arguments.
    scenario.Args.setinstance(DemoArgs())
    if not scenario.Args.getinstance().parse(sys.argv[1:]):
        sys.exit(int(scenario.Args.getinstance().error_code))

    # Main path.
    scenario.Path.setmainpath(scenario.Path(__file__).parents[1])

    # --show-configs option.
    if DemoArgs.getinstance().show_config_db:
        scenario.conf.show(logging.INFO)
        sys.exit(int(scenario.ErrorCode.SUCCESS))

    # Welcome message.
    scenario.logging.info(DemoArgs.getinstance().welcome_message)

    # File logging: use the first scenario file name to determine the output log file name.
    _outpath = DemoArgs.getinstance().scenario_paths[0].with_suffix(".log")
    scenario.conf.set("scenario.log_file", _outpath)
    scenario.logging.info(f"Test log saved in '{_outpath}'")

    # Scenario execution.
    _res = scenario.runner.main()

    # Bye message.
    scenario.logging.info(DemoArgs.getinstance().bye_message)

    # Error code.
    sys.exit(int(_res))
