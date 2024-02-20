# -*- coding: utf-8 -*-

# Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
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

import typing

import scenario

if True:
    from .._paths import SRC_PATH as _SRC_PATH  # `SRC_PATH` used for global variable instanciation.


#: Module paths which local imports should be avoided for.
OPTIMIZED_PATHS = [
    _SRC_PATH / "scenario" / "_args.py",
    _SRC_PATH / "scenario" / "_configdb.py",
    _SRC_PATH / "scenario" / "_configkey.py",
    _SRC_PATH / "scenario" / "_debugutils.py",
    _SRC_PATH / "scenario" / "_enumutils.py",
    _SRC_PATH / "scenario" / "_locations.py",
    _SRC_PATH / "scenario" / "_logextradata.py",
    _SRC_PATH / "scenario" / "_logger.py",
    _SRC_PATH / "scenario" / "_loggingcontext.py",
    _SRC_PATH / "scenario" / "_path.py",
    _SRC_PATH / "scenario" / "_req.py",
    _SRC_PATH / "scenario" / "_reqdb.py",
    _SRC_PATH / "scenario" / "_reqref.py",
    _SRC_PATH / "scenario" / "_reqverifier.py",
    _SRC_PATH / "scenario" / "_scenarioconfig.py",
    _SRC_PATH / "scenario" / "_scenariodefinition.py",
    _SRC_PATH / "scenario" / "_scenariostack.py",
    _SRC_PATH / "scenario" / "_setutils.py",
    _SRC_PATH / "scenario" / "_stepdefinition.py",
]  # type: typing.Sequence[scenario.Path]
