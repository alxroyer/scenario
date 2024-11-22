/*
 * Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


/**
 * @file
 * @brief Menu configurations.
 */


/**
 * @brief Add `.button` class to menu links.
 * @returns {void}
 */
function _scenarioConfigureMenuLinksAsButtons() {
    /** @var {HTMLElement?} */ const _menuDiv = document.getElementById("menu");
    if (_menuDiv) {
        for (/** @var {HTMLElement} */ const _a of _menuDiv.getElementsByClassName("menu")) {
            _a.classList.add("button");
        }
    }
}

// See https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", _scenarioConfigureMenuLinksAsButtons);
} else {
    _scenarioConfigureMenuLinksAsButtons();
}
