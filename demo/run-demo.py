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
        scenario.ScenarioArgs.__init__(self)

        self.setdescription("Demo test launcher.")

        self.welcome_message = "Hello you!"
        self.bye_message = "Bye!"
        self.addarg("Name", "welcome_message", str).define(
            "--welcome", metavar="NAME",
            action="store", type=str,
            help="User name.",
        )

        self.show_config_db = False
        self.addarg("Show configuration database", "show_config_db", bool).define(
            "--show-configs",
            action="store_true",
            help="Show the configuration values with their origin, then stop.",
        )

    def _checkargs(self, args):
        if not super()._checkargs(args):
            return False

        if not self.welcome_message:
            scenario.logging.error("Wrong name '%s'" % self.welcome_message)
            return False
        if not self.welcome_message.startswith("Hello"):
            _name = self.welcome_message
            self.welcome_message = "Hello %s!" % _name
            self.bye_message = "Bye %s!" % _name

        return True


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
    scenario.logging.info("Test log saved in '%s'" % _outpath)

    # Scenario execution.
    _res = scenario.runner.main()

    # Bye message.
    scenario.logging.info(DemoArgs.getinstance().bye_message)

    # Error code.
    sys.exit(int(_res))
