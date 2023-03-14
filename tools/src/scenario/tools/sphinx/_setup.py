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

import sphinx.application


def setup(
        app,  # type: sphinx.application.Sphinx
):  # type: (...) -> None
    """
    This function will be called automatically by the Sphinx application.

    :param app: Sphinx application.
    """
    from ._autodochandlers import AutodocHandlers
    from ._logging import loggingsetup
    from ._sphinxhandlers import SphinxHandlers

    loggingsetup()
    _sphinx_handlers = SphinxHandlers()  # type: SphinxHandlers
    _sphinx_handlers.setup(app)
    _autodoc_handlers = AutodocHandlers()  # type: AutodocHandlers
    _autodoc_handlers.setup(app)
