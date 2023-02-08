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
> limitations under the License.


# scenario

## Purpose

`scenario` is a framework to write and execute scenario tests.

In contrary to a unit test case whose all test methods are assumed to be independant,
a scenario test case is a whole set of ordered steps.
It describes a story from the beginning to the end of the test.

Scenario tests rather fit a functional testing strategy.

One of the main interets of working with `scenario` is its ability to reuse a scenario,
either:
- in initialization conditions steps, to bring the tested item in an appropriate state
  before the test begins,
- or to derivate a nominal scenario in order to write error test cases from the first one.


## Documentation

If generated, the [full documentation](./doc/html/index.html)
is in the 'doc/html' directory.

Use the [tools/mkdoc.py](./tools/mkdoc.py) script to generate the full documentation
(requires a couple of tools).

You may otherwise read through the ReStructured Text source files directly
in the 'doc/src' directory.


## License

TODO: BSD license
