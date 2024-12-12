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
 * @brief Anchors management.
 */


/** @var {object} `scenario.anchors` package. */
scenario.anchors = {};


/**
 * @brief Extracts an anchor name from a URL.
 * @param {string} url URL to extract anchor name from.
 * @returns {string | null} Anchor name if found, `null` otherwise.
 */
scenario.anchors._extractAnchorNameFromUrl = (url) => {
    if (url.includes("#")) {
        return url.substring(url.indexOf("#") + 1);
    } else {
        return null;
    }
};


/**
 * @brief Ensures the appropriate anchor gets the `.focus` class.
 * @param {string} anchorName Name of anchor to set the focus on.
 * @returns {void}
 */
scenario.anchors._setFocus = (anchorName) => {
    for (/** @var {HTMLElement} */ const _focusableDiv of scenario.findNodes(document.body, "div.anchor.focusable")) {
        if (scenario.getNamedObjectIdFromClasses(_focusableDiv, "anchor") === anchorName) {
            console.debug(`Adding .focus class to anchor '${anchorName}'`);
            _focusableDiv.classList.add("focus");
        } else {
            _focusableDiv.classList.remove("focus");
        }
    }
};


// Add `.focus` class on anchor targetted by the current URL.
scenario.onLoad(() => {
    /** @var {string | null} */ const _anchorName = scenario.anchors._extractAnchorNameFromUrl(window.location.href);
    if (_anchorName) {
        console.debug(`Focusing anchor '${_anchorName}' on load`);
        scenario.anchors._setFocus(_anchorName);
    }
});


// Ensure `a.anchor-link`s do modify the `.focus` class when clicked.
scenario.onLoad(() => {
    for (/** @var {HTMLElement} */ const _anchorLink of scenario.findNodes(document.body, "a.anchor-link")) {
        _anchorLink.addEventListener("click", (e) => {
            // Don't prevent default.
            //e.preventDefault();

            /** @var {string | null} */ const _href = _anchorLink.getAttribute("href");
            if (_href) {
                /** @var {string | null} */ const _anchorName = scenario.anchors._extractAnchorNameFromUrl(_href);
                if (_anchorName) {
                    console.debug(`Anchor link '${_anchorName}' clicked`);
                    scenario.anchors._setFocus(_anchorName);
                }
            }
        });
    }
});
