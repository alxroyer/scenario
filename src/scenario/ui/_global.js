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
 * @brief
 *     Ensures `f` be called *on-load*.
 * @param {() => void} f
 *     Function to be called *on-load*.
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
 * @brief
 *     Ensures `raw` HTML class is CSS compatible, as the Python side does.
 * @param {string} raw
 *     Raw HTML class to ensure CSS compatibility for.
 * @returns {string}
 *     CSS compatible HTML class.
 */
scenario.mkCssCompatibleClass = (raw) => {
    return (
        raw
        .replaceAll(".", "-dot-")
        .replaceAll("=", "-eq-")
        .replaceAll("#", "-hash-")
    );
};


/**
 * @brief
 *     Parses a CSS node selector.
 * @param {string} selector
 *     CSS node selector to parse.
 *     Programmatical format, `scenario.mkCssCompatibleClass()` will be called.
 * @returns {{tagName: string | null, id: string | null, classes: string[]}}
 *     Tag name, HTML identifier and/or classes,
 *     classes being CSS-ready, i.e. `scenario.mkCssCompatibleClass()` has been called.
 */
scenario._parseNodeSelector = (selector) => {
    /** @var {RegExpExecArray | null} */ const _match = /([^.#]*)(#(.*)|(\..*)|)/.exec(selector);
    if ((! _match) || (_match.length < 4)) {
        throw SyntaxError(`Invalid node selector '${selector}'`);
    }
    /** @var {string | null} */ const _tagName = _match[1];
    /** @var {string | null} */ const _id = _match[3];
    /** @var {string | null} */ let _classes = _match[4];
    if (_classes) {
        // Ensure `_classes` is space-separated, as `getElementsByClassName()` takes it.
        _classes = _classes.substring(1).replaceAll(".", " ");
        // Ensure `_classes` is "CSS compatible", as the Python side ensured it.
        _classes = scenario.mkCssCompatibleClass(_classes);
    }

    return {
        tagName: _tagName,
        id: _id,
        classes: (_classes ? _classes.split(" ") : []),
    };
};


/**
 * @brief
 *     Checks whether `node` matches with the given `selector`.
 * @param {HTMLElement} node
 *     Node to check match with `selector`.
 * @param {string | {tagName: string | null, id: string | null, classes: string[]}} selector
 *     Single node CSS selector.
 *     Programmatical format in case of a string, `scenario.mkCssCompatibleClass()` will be called.
 *     As returned by `scenario._parseNodeSelector()` otherwise.
 * @param {boolean | undefined} debug
 *     `true` to activate debugging.
 * @param {string | undefined} indentation
 *     Debugging indentation.
 * @returns {boolean}
 *     `true` for a match, `false` otherwise.
 */
scenario.nodeMatches = (node, selector, {debug, indentation} = {}) => {
    // Default parameter values.
    debug = debug || false;
    indentation = indentation || "";

    /**
     * @brief Prints out a debug line depending on `debug`.
     * @param {string} text Debug line.
     * @returns {void}
     */
    function _debug(text) {
        if (debug) {
            console.debug(`${indentation}scenario.nodeMatches(): ${text}`);
        }
    }

    _debug(`scenario.nodeMatches(${node}, ${selector})`);

    // Parse `selector` if needed.
    if (typeof(selector) === "string") {
        selector = scenario._parseNodeSelector(selector);
        _debug(`'${selector}' => tag name: ${selector.tagName}, id: ${selector.id}, classes: [${selector.classes}]`);
    }

    // Check tag name.
    if (selector.tagName && (node.tagName.toLowerCase() !== selector.tagName.toLowerCase())) {
        _debug(`Tag name ${node.tagName} !== ${selector.tagName} => discarded`);
        return false;
    }
    // Check HTML identifier.
    if (selector.id && (node.id !== selector.id)) {
        _debug(`Id ${node.id} !== ${selector.id} => discarded`);
        return false;
    }
    // Check classes.
    if (selector.classes.length) {
        for (/** @var {string} */ const _class of selector.classes) {
            if (! node.classList.contains(_class)) {
                _debug(`Missing class '${_class}' in [${node.classList}] => discarded`);
                return false;
            }
        }
    }

    _debug("=> match");
    return true;
};


/**
 * @brief
 *     Finds nodes matching with `selector`.
 * @param {HTMLElement} node
 *     Current node.
 * @param {string} selector
 *     CSS selector.
 *     Programmatical format, `scenario.mkCssCompatibleClass()` will be called.
 * @param {boolean | undefined} debug
 *     `true` to activate debugging.
 * @param {string | undefined} indentation
 *     Debugging indentation.
 * @returns {HTMLElement[]}
 *     Nodes matching `selector`.
 */
scenario.findNodes = (node, selector, {debug, indentation}={}) => {
    // Default parameter values.
    debug = debug || false;
    indentation = indentation || "";

    /**
     * @brief Prints out a debug line depending on `debug`.
     * @param {string} text Debug line.
     * @returns {void}
     */
    function _debug(text) {
        if (debug) {
            console.debug(`${indentation}scenario.findNodes(): ${text}`);
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
    /** @var {{id: string | null, tagName: string | null, classes: string[]}} */ const _selector = scenario._parseNodeSelector(_selectors[0]);
    _debug(`'${_selectors[0]}' => tag name: ${_selector.tagName}, id: ${_selector.id}, classes: [${_selector.classes}]`);

    // - Find node(s) from the most representative criteria:
    /** @var {HTMLElement[]} */ let _selected = [];
    if (_selector.id) {
        /** @var {HTMLElement | null} */ const _identified = document.getElementById(_selector.id);
        if (_identified) {
            _selected.push(_identified);
        }
        _debug(`id='${_selector.id}' => ${_selected}`);
    } else if (_selector.classes.length) {
        // Memo:
        //   Use `getElementsByClassName()` before `getElementsByTagName()`.
        //   If classes are given, this criteria should normally be more restrictive, thus faster.
        _selected.push(...node.getElementsByClassName(_selector.classes.join(" ")));
        _debug(`classes='${_selector.classes.join(" ")}' => ${_selected}`);
    } else if (_selector.tagName) {
        _selected.push(...node.getElementsByTagName(_selector.tagName));
        _debug(`tagName='${_selector.tagName}' => ${_selected}`);
    } else {
        throw SyntaxError(`Invalid selector '${_selectors[0]}'`);
    }

    // - Then check the nodes selected above pass all criteria:
    _selected = _selected.filter((e) => {
        if (! scenario.nodeMatches(e, _selector, {debug: debug, indentation: `${indentation}  `})) {
            return false;
        }
        return true;
    });
    _debug(`'${_selectors[0]}' => ${_selected}`);

    // If that was the end of the selector, then this is a final recursion call.
    // Return selected nodes right now.
    if (_selectors.length === 1) {
        _debug(`=> ${_selected}`);
        return _selected;
    }

    // Otherwise, make recursive calls, and return the nodes selected from final recursive calls.
    /** @var {HTMLElement[]} */ const _final = [];
    for (const _node of _selected) {
        _final.push(...scenario.findNodes(_node, _selectors.slice(1).join(" "), {debug: debug, indentation: `${indentation}  `}));
    }
    _debug(`=> ${_final}`);
    return _final;
};


/**
 * @brief
 *     Search for a CID (class identifier, i.e. "<type>=<cid>" class) in `node`'s HTML classes.
 * @param {HTMLElement} node
 *     Node to read classes from.
 * @param {string} type
 *     Type of CID to search.
 * @returns {string | null}
 *     CID value if found, `null` otherwise.
 */
scenario.getCid = (node, type) => {
    /** @var {string} */ const _starter = scenario.mkCssCompatibleClass(`${type}=`);
    for (/** @var {string} */ const _class of node.classList) {
        if (_class.startsWith(_starter)) {
            return _class.substring(_starter.length);
        }
    }
    return null;
};


/**
 * @brief
 *     Finds one class of `classes` in HTML classes of `node`.
 * @param {HTMLElement} node
 *     Node to read HTML classes from.
 * @param {string[]} classes
 *     Candidate HTML classes to search.
 *     Programmatical format, `scenario.mkCssCompatibleClass()` will be called.
 * @returns {string | null}
 *     First class of `classes` found in HTML classes of `node`, or `null` if none found.
 *     Programmatical format, `scenario.mkCssCompatibleClass()` not called on it.
 */
scenario.findOneClassOf = (node, classes) => {
    for (/** @var {string} */ const _class of classes) {
        if (node.classList.contains(scenario.mkCssCompatibleClass(_class))) {
            return _class;
        }
    }
    return null;
};
