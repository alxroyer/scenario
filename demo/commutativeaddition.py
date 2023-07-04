# -*- coding: utf-8 -*-

import scenario


class CommutativeAddition(scenario.Scenario):

    def __init__(self, a=1, b=3):
        scenario.Scenario.__init__(
            self,
            title="Commutative addition",
            description="Addition of two members, swapping orders.",
        )

        self.a = a
        self.b = b
        self.result1 = 0
        self.result2 = 0

    def step000(self):
        self.STEP("Initial conditions")

        if self.ACTION(f"Let a = {self.a}, and b = {self.b}"):
            self.evidence(f"a = {self.a}")
            self.evidence(f"b = {self.b}")

    def step010(self):
        self.STEP("a + b")

        if self.ACTION("Compute (a + b) and store the result as result1."):
            self.result1 = self.a + self.b
            self.evidence(f"result1 = {self.result1}")

    def step020(self):
        self.STEP("b + a")

        if self.ACTION("Compute (b + a) and store the result as result2."):
            self.result2 = self.b + self.a
            self.evidence(f"result2 = {self.result2}")

    def step030(self):
        self.STEP("Check")

        if self.ACTION("Compare result1 and result2."):
            pass
        if self.RESULT("result1 and result2 are the same."):
            self.assertequal(self.result1, self.result2)
            self.evidence(f"{self.result1} == {self.result2}")
