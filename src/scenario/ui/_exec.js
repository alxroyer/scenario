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


// Execution.

/**
 * @brief Installs event listeners for execution buttons.
 * @returns {void}
 */
function _scenarioConfigureExecButtons() {
    for (/** @var {HTMLElement} */ const _button of document.getElementsByClassName("exec button")) {
        _button.addEventListener("click", function(e) {
            e.preventDefault();

            _scenarioExec(this.getAttribute("href"));
        });
    }
}
_scenarioConfigureExecButtons();

/**
 * @brief Executes a scenario action.
 * @param {string} url Action URL.
 * @returns {void}
 */
function _scenarioExec(url) {
    // Process the given URL.
    console.debug(`Executing '${url}'...`);
    const _xmlHttp = new XMLHttpRequest();
    _xmlHttp.open(
        "GET", url,
        false,  // Synchronous request.
    );
    _xmlHttp.send();
    console.debug(`'${url}' returned '${_xmlHttp.responseText}'`);

    // Parse the JSON execution result.
    const _json = JSON.parse(_xmlHttp.responseText);

    // Show execution result.
    scenarioShowExecResultPopup(_json.title, _json.text);
}


// Execution result.

/** @var {boolean} Tells whether the `.exec-result` popup div shall be used. `alert()` called otherwise. */
let scenarioUseExecResultDivPopup = false;
/** @var {HTML.Element} `.exec-result` popup div element. */
const _scenarioExecResultDivPopup = document.getElementById("exec-result");

/**
 * @brief Displays execution results.
 * @param {string} title Action title.
 * @param {string} text Execution result as plain text.
 * @returns {void}
 */
function scenarioShowExecResultPopup(title, text) {
    console.debug(`Displaying exec result popup with title='${title}' and text='${text}'`);

    if (scenarioUseExecResultDivPopup) {
        // Set popup title.
        for (/** @var {HTMLElement} */ const _titleDiv of _scenarioExecResultDivPopup.getElementsByClassName("title")) {
            _titleDiv.textContent = title;
        }
        // Set popup content.
        for (/** @var {HTMLElement} */ const _textDiv of _scenarioExecResultDivPopup.getElementsByClassName("text")) {
            _textDiv.textContent = text;
        }

        // Display the popup.
        _scenarioExecResultDivPopup.style.display = "block";
    } else {
        // Display the message with `alert()`.
        alert(`[${title}]\n\n${text}`);

        // Refresh the page.
        _scenarioRefreshCurrentPage();
    }
}

/**
 * @brief Installs the event listener for the OK button in the `.exec-result` popup div.
 * @returns {void}
 */
function _scenarioConfigureExecResultOkButton() {
    for (/** @var {HTMLElement} */ const _button of _scenarioExecResultDivPopup.getElementsByClassName("exec-result button validate")) {
        _button.addEventListener("click", function(e) {
            e.preventDefault();

            // Hide the popup.
            console.debug("Hiding execution result popup");
            _scenarioExecResultDivPopup.style.display = "none";

            // Refresh the page.
            _scenarioRefreshCurrentPage();
        });
    }
}
_scenarioConfigureExecResultOkButton();


// Refresh.

/**
 * @brief Refreshes the current page after execution result has been displayed.
 * @returns {void}
 */
function _scenarioRefreshCurrentPage() {
    console.debug("Refreshing the page");
    window.location.reload();
}
