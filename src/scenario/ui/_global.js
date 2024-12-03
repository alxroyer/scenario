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
 * @brief Global `scenario` variables and functions.
 */


/** @var {object} `scenario` package. */
let scenario = {};

/**
 * @brief Ensures `f` be called *on-load*.
 * @param {() => void} f Function to be called *on-load*.
 * @returns {void}
 */
scenario.onLoad = (f) => {
    // See https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event
    if (document.readyState === "loading") {
        // Document not loaded yet => register `f` with an event listener.
        document.addEventListener("DOMContentLoaded", f);
    } else {
        // Document already loaded => call `f()` straight away.
        f();
    }
};
