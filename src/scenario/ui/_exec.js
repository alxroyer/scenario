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
 * @brief Action executions.
 */


/** @var {object} `scenario.exec` package. */
scenario.exec = {};


// Execution.

// Install event listeners for execution buttons.
scenario.onLoad(() => {
    for (/** @var {HTMLElement} */ const _button of document.getElementsByClassName("exec button")) {
        _button.addEventListener("click", (e) => {
            e.preventDefault();

            scenario.exec._execute(_button.getAttribute("href"));
        });
    }
});

/**
 * @brief Executes a scenario action.
 * @param {string} url Action URL.
 * @returns {void}
 */
scenario.exec._execute = (url) => {
    // Process the given URL asynchronously.
    // Inspired from https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest_API/Synchronous_and_Asynchronous_Requests.
    console.debug(`Executing '${url}'...`);

    /** @var {XMLHttpRequest} */ const _req = new XMLHttpRequest();
    _req.open(
        "GET", url,
        true,  // Asynchronous request.
    );
    /** @var {string} */ let _title = `Request '${url}' error`;
    /** @var {string} */ let _message = "";
    _req.onload = (e) => {
        // Check state is DONE (see https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/readyState).
        if (_req.readyState !== 4) {
            _message = `Request '${url}' bad state ${_req.status}`;
            console.error(_message);
        } else {
            _message = `Request '${url}' returned ${_req.status} - ${_req.statusText}`;

            // Check HTTP status is OK.
            if (_req.status !== 200) {
                console.error(_message);
            } else {
                console.debug(_message);

                // Parse the JSON execution result.
                console.debug(`JSON content: '${_req.responseText}'`);
                /** @var {object} */ const _json = JSON.parse(_req.responseText);
                _title = _json.title;
                _message = _json.text;
            }
        }

        // Show execution result.
        scenario.exec.showResult(_title, _message);
    };
    _req.onerror = (e) => {
        scenario.exec.showResult(_title, _req.statusText);
    };
    _req.send();
};


// Execution result.

/** @var {boolean} Tells whether the `.exec-result` popup div shall be used. `alert()` called by default. */
scenario.exec.useExecResultPopupDiv = false;

/**
 * @brief Displays execution results.
 * @param {string} title Action title.
 * @param {string} text Execution result as plain text.
 * @returns {void}
 */
function scenarioShowExecResultPopup(title, text) {
    console.debug(`Displaying execution result popup with title='${title}' and text='${text}'`);

    /** @var {HTMLElement?} */ const _resultDiv = document.getElementById("exec-result");
    if (scenario.exec.useExecResultPopupDiv && _resultDiv) {
        // Set popup title.
        for (/** @var {HTMLElement} */ const _titleDiv of _resultDiv.getElementsByClassName("title")) {
            _titleDiv.textContent = title;
        }
        // Set popup content.
        for (/** @var {HTMLElement} */ const _textDiv of _resultDiv.getElementsByClassName("text")) {
            _textDiv.textContent = text;
        }

        // Display the popup.
        _resultDiv.style.display = "block";
    } else {
        // Display the message with `alert()`.
        alert(`[${title}]\n\n${text}`);

        // Refresh the page.
        scenario.exec._refreshCurrentPage();
    }
}

// Install the event listener for the OK button in the `.exec-result` popup div.
scenario.onLoad(() => {
    /** @var {HTMLElement?} */ const _resultDiv = document.getElementById("exec-result");
    if (_resultDiv) {
        for (/** @var {HTMLElement} */ const _button of _resultDiv.getElementsByClassName("exec-result button validate")) {
            _button.addEventListener("click", (e) => {
                e.preventDefault();

                // Hide the popup.
                console.debug("Hiding execution result popup");
                _resultDiv.style.display = "none";

                // Refresh the page.
                scenario.exec._refreshCurrentPage();
            });
        }
    }
});


// Refresh.

/**
 * @brief Refreshes the current page after execution result has been displayed.
 * @returns {void}
 */
scenario.exec._refreshCurrentPage = () => {
    console.debug(`Refreshing page '${window.location.href}'`);

    // Avoid reloading POST pages with parameters.
    // Inspired from https://stackoverflow.com/questions/1226714/how-to-get-the-browser-to-navigate-to-url-in-javascript#1226718
    //window.location.reload();
    window.location.href = window.location.href;
};
