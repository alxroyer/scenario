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
 * @brief Extracts an anchor CID from a URL.
 * @param {string} url URL to extract anchor CID from.
 * @returns {string | null} Anchor CID if found, `null` otherwise.
 */
scenario.anchors._extractAnchorCidFromUrl = (url) => {
    if (url.includes("#")) {
        /** @var {string} */ const _cid = url.substring(url.indexOf("#") + 1);
        console.debug(`scenario.anchors._extractAnchorCidFromUrl('${url}') => '${_cid}'`);
        return _cid;
    } else {
        return null;
    }
};


/**
 * @brief Ensures the appropriate anchor gets the `.focus` class.
 * @param {string} anchorCid CID of anchor to set the focus on.
 * @returns {void}
 */
scenario.anchors._setFocus = (anchorCid) => {
    for (/** @var {HTMLElement} */ const _focusableDiv of scenario.findNodes(document.body, "div.anchor.focusable")) {
        if (scenario.getCid(_focusableDiv, "anchor") === anchorCid) {
            // In case the anchor is hidden in a collapsed row.
            scenario.tables.ensureExpanded(_focusableDiv);

            console.debug(`Adding .focus class to anchor '${anchorCid}'`);
            _focusableDiv.classList.add("focus");

            // Ensure the anchor is visible.
            _focusableDiv.scrollIntoView();
            // Scroll a couple of pixels backward to avoid the anchor being stuck with the top of the window.
            window.scrollBy(0, -20);
        } else {
            _focusableDiv.classList.remove("focus");
        }
    }
};


// Add `.focus` class on anchor targetted by the current URL.
scenario.onLoad(() => {
    /** @var {string | null} */ const _anchorCid = scenario.anchors._extractAnchorCidFromUrl(window.location.href);
    if (_anchorCid) {
        console.debug(`Focusing anchor '${_anchorCid}' on load`);
        scenario.anchors._setFocus(_anchorCid);
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
                /** @var {string | null} */ const _anchorCid = scenario.anchors._extractAnchorCidFromUrl(_href);
                if (_anchorCid) {
                    console.debug(`Anchor link '${_anchorCid}' clicked`);
                    scenario.anchors._setFocus(_anchorCid);
                }
            }
        });
    }
});
