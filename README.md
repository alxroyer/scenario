# scenario

## Purpose

The *scenario* library is a framework for writing and executing full campaigns of tests,
with human-readable documentation.

A *scenario* test case is a sequence of *steps*, executed one after the others,
defining a *story* by the way.

---

One of the main interests of *scenario* is its ability to *reuse test code*:
- [Step objects](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.step-objects.html):
  Instanciate steps  one after the others, just like bricks,
  and quickly write different versions of a story
  (like a nominal test scenario, then alternative scenarios).
- [Subscenarios](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.subscenarios.html):
  Reuse existing test cases as subscenario utils,
  a fair way to set up initial conditions for instance.

Another strength of the *scenario* framework is its *documentation facilities*:
- Tie the test documentation (actions, expected results) right next to the related test code
  (see example below for an overview).
  By the way, the code is more understandable, and the whole easier to maintain.
- Easily collect test [evidence](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.evidence.html),
  just by using the [assertion API](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.assertions.html) provided.
- Use [execution reports](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.reports.html)
  to generate deliverable documentation in the end.

---

*scenario* also comes with a set of high quality features,
making tests easier to write and maintain:

- Rich [assertion API](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.assertions.html),
  with [evidence](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.evidence.html) collection (as introduced above).
- Powerful [logging system](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.logging.html),
  with class loggers, indentation and colorization.
- Handful [configuration facilities](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.config-db.html).
- [Campaign](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.campaigns.html) definition and execution.
- [Scenario](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.reports.html)
  and [campaign reports](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.campaigns.html#campaign-reports).
- [Stability](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.stability.html) investigation tools.
- Flexible [known issue](https://scenario-testing-framework.readthedocs.io/en/latest/advanced.known-issues.html) and test workaround tracking.
- ...


## Example

Please refer to the [quickstart documenation](https://scenario-testing-framework.readthedocs.io/en/latest/quickstart.html)
for details on the example below.

```Python
# -*- coding: utf-8 -*-

import scenario


class CommutativeAddition(scenario.Scenario):

    SHORT_TITLE = "Commutative addition"
    TEST_GOAL = "Addition of two members, swapping orders."

    def __init__(self, a=1, b=3):
        scenario.Scenario.__init__(self)
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
```


## Documentation

See the [online documentation](https://scenario-testing-framework.readthedocs.io/).

> **Disclaimer**
>
> The documentation is not complete yet.
> A couple of chapters still need to be filled in or improved.
> Feel free to contribute on that point (see issue [#13](https://github.com/alxroyer/scenario/issues/13)).

## License

> Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
>
> Licensed under the Apache License, Version 2.0 (the "License");
> you may not use this file except in compliance with the License.
> You may obtain a copy of the License at
>
>     http://www.apache.org/licenses/LICENSE-2.0
>
> Unless required by applicable law or agreed to in writing, software
> distributed under the License is distributed on an "AS IS" BASIS,
> WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
> See the License for the specific language governing permissions and
> limitations under the License
