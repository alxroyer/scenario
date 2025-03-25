# -*- coding: utf-8 -*-

import scenario


class MyLogger(scenario.Logger):

    def __init__(self):
        scenario.Logger.__init__(self, "My logger")


class LoggingScenario(scenario.Scenario):

    def __init__(self):
        scenario.Scenario.__init__(
            self,
            title="Logging demo",
            description="Demonstrate logging facilities.",
        )

        self.class_logger = MyLogger()
        self.class_logger.setlogcolor(scenario.Console.Color.LIGHTBLUE36)

    def step010(self):
        self.STEP("Logging with the main logger")

        if self.ACTION("Log messages of different log levels with the main logger."):
            scenario.logging.error("This is an error!!!")
            scenario.logging.warning("This is a warning!")
            scenario.logging.info("This is information.")
            scenario.logging.debug("This is debug.")

    def step020(self):
        self.STEP("Logging with the scenario instance")

        if self.ACTION("Log messages of different log levels with the scenario itself."):
            self.error("This is an error!!!")
            self.warning("This is a warning!")
            self.info("This is information.")
            self.debug("(This is debug.)")

    def step030(self):
        self.STEP("Logging with a class logger")

        if self.ACTION("Log messages of different log levels with the class logger instance."):
            self.class_logger.error("This is an error!!!")
            self.class_logger.warning("This is a warning!")
            self.class_logger.info("This is information.")
            self.class_logger.debug("(This is debug.)")

        if self.ACTION("Activate debugging for the class logger instance."):
            self.class_logger.enabledebug(True)

        if self.ACTION("Log a debug message again with the class logger instance."):
            self.class_logger.debug("(This is debug again.)")

    def step110(self):
        self.STEP("Class logger indentation")

        if self.ACTION("Enable debugging with the class logger, and log something with it."):
            self.class_logger.enabledebug(True)
            self.class_logger.info("Hello")
        try:
            for _ in range(3):
                if self.ACTION("Push indentation to the class logger."):
                    self.class_logger.pushindentation()
                if self.ACTION("Log something with the class logger."):
                    self.class_logger.info("Hello")
            if self.ACTION("Pop indentation from the class logger."):
                self.class_logger.popindentation()
            if self.ACTION("Log something with the class logger."):
                self.class_logger.info("Hello")
        finally:
            if self.ACTION("Reset the class logger indentation."):
                self.class_logger.resetindentation()
            if self.ACTION("Log something with the class logger."):
                self.class_logger.info("Hello")

    def step120(self):
        self.STEP("Main logger indentation")

        _expected = {"a": [0], "b": [1, 2, 3, 4]}

        _results = {}
        if self.ACTION("Retrieve results."):
            _results = _expected.copy()
        if self.RESULT(f"Results contain {len(_expected)} keys:"):
            self.assertlen(_results, len(_expected), evidence=True)
        for _key in _expected:
            if self.RESULT(f"- Key {_key!r}, with {len(_expected[_key])} values:"):
                self.assertlen(_results[_key], len(_expected[_key]), evidence=True)
            # Indent each value below the related key.
            with scenario.logging.pushindentation("  "):
                for _index, _value in enumerate(_expected[_key]):
                    if self.RESULT(f"- Value #{_index+1} is {_value!r}"):
                        self.assertequal(_results[_key][_index], _expected[_key][_index], evidence=True)
