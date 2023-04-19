# -*- coding: utf-8 -*-

import pathlib
import scenario
import sys

sys.path.append(str(pathlib.Path(__file__).parent))
from commutativeaddition import CommutativeAddition  # noqa  ## Module level import not at top of file


class CommutativeAdditions(scenario.Scenario):

    SHORT_TITLE = "Commutative additions"
    TEST_GOAL = "Call the CommutativeAddition scenario with different inputs."

    def step010(self):
        self.STEP("Both positive members")

        if self.ACTION("Launch the CommutativeAddition scenario with 4 and 5 for inputs."):
            _scenario = CommutativeAddition(4, 5)
            scenario.runner.executescenario(_scenario)

    def step020(self):
        self.STEP("Positive and negative members")

        if self.ACTION("Launch the CommutativeAddition scenario with -1 and 3 for inputs."):
            _scenario = CommutativeAddition(-1, 3)
            scenario.runner.executescenario(_scenario)

    def step030(self):
        self.STEP("Both negative members")

        if self.ACTION("Launch the CommutativeAddition scenario with -1 and -7 for inputs."):
            _scenario = CommutativeAddition(-1, -7)
            scenario.runner.executescenario(_scenario)
