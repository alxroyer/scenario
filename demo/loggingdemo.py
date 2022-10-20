# -*- coding: utf-8 -*-

import scenario


class MyLogger(scenario.Logger):

    def __init__(self):
        scenario.Logger.__init__(self, "My logger")


class LoggingScenario(scenario.Scenario):

    SHORT_TITLE = "Logging demo"
    TEST_GOAL = "Demonstrate logging facilities."

    def __init__(self):
        scenario.Scenario.__init__(self)
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
            self.debug("This is debug.")

    def step030(self):
        self.STEP("Logging with a class logger")

        if self.ACTION("Log messages of different log levels with the class logger instance."):
            self.class_logger.error("This is an error!!!")
            self.class_logger.warning("This is a warning!")
            self.class_logger.info("This is information.")
            self.class_logger.debug("This is debug.")

        if self.ACTION("Activate debugging for the class logger instance."):
            self.class_logger.enabledebug(True)

        if self.ACTION("Log a debug message again with the class logger instance."):
            self.class_logger.debug("This is debug again.")

    def step110(self):
        self.STEP("Class logger indentation")

        if self.ACTION("Log something with the class logger."):
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

        if self.ACTION("Log something with the main logger."):
            scenario.logging.info("Hello")
        try:
            for _ in range(3):
                if self.ACTION("Push indentation to the main logger."):
                    scenario.logging.pushindentation()
                if self.ACTION("Log something with the main logger."):
                    scenario.logging.info("Hello")
            if self.ACTION("Pop indentation from the main logger."):
                scenario.logging.popindentation()
            if self.ACTION("Log something with the main logger."):
                scenario.logging.info("Hello")
        finally:
            if self.ACTION("Reset the main logger indentation."):
                scenario.logging.resetindentation()
            if self.ACTION("Log something with the main logger."):
                scenario.logging.info("Hello")
