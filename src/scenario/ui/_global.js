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


/**
 * @brief Finds nodes matching `selector`.
 * @param {HTMLElement} node Current node.
 * @param {string} selector CSS selector.
 * @returns {HTMLElement[]} Nodes matching `selector`.
 */
scenario.findNodes = (node, selector, {debug=false, indentation=""}={}) => {
    function _debug(text) {
        if (debug) {
            console.debug(`${indentation}${text}`);
        }
    }

    _debug(`scenario.findNodes(node=${node}, selector='${selector}')`);

    // Parse `selector`.
    // If no selector, return empty node list (defensive code).
    if (! selector) {
        return [];
    }
    /** @var {string[]} */ const _selectors = selector.split(" ");
    if ((! _selectors) || (! _selectors[0])) {
        return [];
    }

    // Search next nodes from `_selectors[0]`:
    // - Parse `_selectors[0]`.
    /** @var {(HTMLElement | null)[]} */ let _selected = [];
    /** @var {RegExpExecArray | null} */ const _match = /([^.#]*)(#(.*)|(\..*)|)/.exec(_selectors[0]);
    if ((! _match) && (_match.length < 4)) {
        throw SyntaxError(`Invalid selector '${_selectors[0]}'`);
    }
    /** @var {string | null} */ const _tagName = _match[1];
    /** @var {string | null} */ const _id = _match[3];
    /** @var {string | null} */ const _classes = _match[4];
    _debug(`scenario.findNodes(): '${_selectors[0]}' => _tagName: ${_tagName}, _id: ${_id}, _classes: ${_classes}`);
    // - Find node(s) from the most representative criteria:
    if (_id) {
        _selected.push(document.getElementById(_id));
    } else if (_classes) {
        _selected.push(...node.getElementsByClassName(_classes.substring(1).replace(".", " ")));
    } else if (_tagName) {
        _selected.push(...node.getElementsByTagName(_tagName));
    } else {
        throw SyntaxError(`Invalid selector '${_selectors[0]}'`);
    }
    // - Then check the nodes selected above pass all criteria:
    _selected = _selected.filter((e) => {
        if (! e) {
            return false;
        }
        if (_tagName && (e.tagName.toLowerCase() !== _tagName.toLowerCase())) {
            return false;
        }
        if (_classes) {
            for (/** @var {string} */ const _class of _classes.substring(1).split(".")) {
                if (! e.classList.contains(_class)) {
                    return false;
                }
            }
        }
        return true;
    });
    _debug(`scenario.findNodes(): '${_selectors[0]}' => ${_selected}`);

    // If that was the end of the selector, then this is a final recursion call.
    // Return selected nodes right now.
    if (_selectors.length === 1) {
        _debug(`scenario.findNodes() => ${_selected}`);
        return _selected;
    }

    // Otherwise, make recursive calls, and return the nodes selected from final recursive calls.
    /** @var {HTMLElement[]} */ const _final = [];
    for (const _node of _selected) {
        _final.push(...scenario.findNodes(_node, _selectors.slice(1).join(" "), {debug: debug, indentation: `${indentation}  `}));
    }
    _debug(`scenario.findNodes() => ${_final}`);
    return _final;
};


/**
 * @brief Search for a named object identifier (i.e. "<name>=<value>") in `node`'s classes.
 * @param {HTMLElement} node Node to read classes from.
 * @param {string} name Name of the class to search.
 * @returns {string | null} Named class value if found, `null` otherwise.
 */
scenario.getNamedObjectIdFromClasses = (node, name) => {
    /** @var {string} */ const _starter = `${name}=`;
    for (/** @var {string} */ const _class of node.classList) {
        if (_class.startsWith(_starter)) {
            return _class.substring(_starter.length);
        }
    }
    return null;
};


/**
 * @brief Select file(s).
 * @param {string?} contentType The content type of files you wish to select. For instance, use "image/*" to select all types of images.
 * @param {boolean?} multiple Indicates if the user can select multiple files.
 * @returns {Promise<File|File[]>} A promise of a file or array of files in case the multiple parameter is true.
 *
 * Inspired from:
 * - https://stackoverflow.com/questions/16215771/how-to-open-select-file-dialog-via-js#40971885
 * - https://stackoverflow.com/questions/16215771/how-to-open-select-file-dialog-via-js#52757538
 *
 * @warning Can't be used to determine local absolute paths.
 *     For security reasons, Javascript can't do such a thing.
 *     Gives access to base file name and file content, but not the full path.
 */
scenario.selectFile$ = ({contentType, multiple} = {contentType: undefined, multiple: false}) => {
    // Check input arguments.
    if (multiple === undefined) {
        multiple = false;
    }

    return new Promise((resolve, reject) => {
        /** @var {HTMLElement} */ let _input = document.createElement("input");
        _input.type = "file";
        _input.multiple = multiple;
        _input.accept = contentType;

        _input.onchange = () => {
            /** @var {File[]} */ let files = Array.from(_input.files);
            if (multiple) {
                resolve(files);
            } else {
                resolve(files[0]);
            }
        };

        _input.click();
    });
};
