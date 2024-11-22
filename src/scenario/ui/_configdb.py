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

"""
:mod:`scenario.ui` configurations.
"""

import scenario


class UIConfig(scenario.Logger):
    """
    `scenario.ui` configuration management.

    Instantiated once with the :data:`UI_CONFIG` singleton.

    This class defines methods that help reading `scenario.ui` configurations:
    from the program arguments (see: :class:`._args.UIArgs`),
    and the `scenario` configuration database (see: :class:`scenario._configdb.ConfigDatabase`).
    """

    class Key(scenario.enum.StrEnum):
        """
        `scenario` configuration keys.
        """

        #: Main path for `scenario.ui` execution. Absolute path string. Default is 'ui/' in the :mod:`scenario` repository directory.
        MAIN_PATH = "scenario.ui.main_path"
        #: `scenario.ui` favicon URL. String. Defaults to ``data:...`` specification.
        FAVICON_URL = "scenario.ui.favicon_url"
        #: Main `scenario.ui` CSS URL. String. Defaults to 'css/ui.css'.
        CSS_URL = "scenario.ui.css_url"
        #: Main `scenario.ui` Javascript URL. String. Default to 'js/ui.js'.
        JS_URL = "scenario.ui.js_url"

    def __init__(self):  # type: (...) -> None
        """
        Initializes the instance as a logger.
        """
        from ._debugclasses import UIDebugClass

        scenario.Logger.__init__(self, UIDebugClass.CONFIG_DB)

    def mainpath(self):  # type: (...) -> scenario.Path
        """
        Retrieves the working directory path for `scenario.ui`.

        :return: `scenario.ui` main working directory.
        """
        from .._path import ROOT_SCENARIO_PATH  # Access `scenario` inner symbols.

        _abspath = (
            scenario.conf.get(self.Key.MAIN_PATH, type=str)
            or (ROOT_SCENARIO_PATH / "ui").abspath
        )  # type: str
        self.debug("uimainpath() -> %r", scenario.Path(_abspath))
        return scenario.Path(_abspath)

    def faviconurl(self):  # type: (...) -> str
        """
        Retrieves the URL for the `scenario.ui` favicon.

        :return: URL from :attr:`UIConfig.Key.MAIN_PATH`, or ``data:`` URL.
        """
        _favicon_url = scenario.conf.get(
            self.Key.FAVICON_URL, type=str,
            # Inspired from https://stackoverflow.com/questions/1321878/how-to-prevent-favicon-ico-requests#13416784
            default="data:;base64,=",
        )  # type: str
        self.debug("faviconurl() -> %r", _favicon_url)
        return _favicon_url

    def cssurl(self):  # type: (...) -> str
        """
        Retrieves the URL for the main `scenario.ui` CSS file.

        :return: URL from :attr:`UIConfig.Key.MAIN_PATH`.
        """
        _css_url = scenario.conf.get(self.Key.CSS_URL, type=str, default="css/ui.css")  # type: str
        self.debug("cssurl() -> %r", _css_url)
        return _css_url

    def jsurl(self):  # type: (...) -> str
        """
        Retrieves the URL for the main `scenario.ui` Javascript file.

        :return: URL from :attr:`UIConfig.Key.MAIN_PATH`.
        """
        _js_url = scenario.conf.get(self.Key.JS_URL, type=str, default="js/ui.js")  # type: str
        self.debug("jsurl() -> %r", _js_url)
        return _js_url


#: Main instance of :class:`UIConfig`.
UI_CONFIG = UIConfig()  # type: UIConfig
