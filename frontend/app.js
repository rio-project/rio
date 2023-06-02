// modules are defined as an array
// [ module function, map of requires ]
//
// map of requires is short require name -> numeric require
//
// anything defined in a previous bundle is accessed via the
// orig method which is the require for previous bundles
parcelRequire = (function (modules, cache, entry, globalName) {
    // Save the require from previous bundle to this closure if any
    var previousRequire = typeof parcelRequire === 'function' && parcelRequire;
    var nodeRequire = typeof require === 'function' && require;

    function newRequire(name, jumped) {
        if (!cache[name]) {
            if (!modules[name]) {
                // if we cannot find the module within our internal map or
                // cache jump to the current global require ie. the last bundle
                // that was added to the page.
                var currentRequire =
                    typeof parcelRequire === 'function' && parcelRequire;
                if (!jumped && currentRequire) {
                    return currentRequire(name, true);
                }

                // If there are other bundles on this page the require from the
                // previous one is saved to 'previousRequire'. Repeat this as
                // many times as there are bundles until the module is found or
                // we exhaust the require chain.
                if (previousRequire) {
                    return previousRequire(name, true);
                }

                // Try the node require function if it exists.
                if (nodeRequire && typeof name === 'string') {
                    return nodeRequire(name);
                }

                var err = new Error("Cannot find module '" + name + "'");
                err.code = 'MODULE_NOT_FOUND';
                throw err;
            }

            localRequire.resolve = resolve;
            localRequire.cache = {};

            var module = (cache[name] = new newRequire.Module(name));

            modules[name][0].call(
                module.exports,
                localRequire,
                module,
                module.exports,
                this
            );
        }

        return cache[name].exports;

        function localRequire(x) {
            return newRequire(localRequire.resolve(x));
        }

        function resolve(x) {
            return modules[name][1][x] || x;
        }
    }

    function Module(moduleName) {
        this.id = moduleName;
        this.bundle = newRequire;
        this.exports = {};
    }

    newRequire.isParcelRequire = true;
    newRequire.Module = Module;
    newRequire.modules = modules;
    newRequire.cache = cache;
    newRequire.parent = previousRequire;
    newRequire.register = function (id, exports) {
        modules[id] = [
            function (require, module) {
                module.exports = exports;
            },
            {},
        ];
    };

    var error;
    for (var i = 0; i < entry.length; i++) {
        try {
            newRequire(entry[i]);
        } catch (e) {
            // Save first error but execute all entries
            if (!error) {
                error = e;
            }
        }
    }

    if (entry.length) {
        // Expose entry point to Node, AMD or browser globals
        // Based on https://github.com/ForbesLindesay/umd/blob/master/template.js
        var mainExports = newRequire(entry[entry.length - 1]);

        // CommonJS
        if (typeof exports === 'object' && typeof module !== 'undefined') {
            module.exports = mainExports;

            // RequireJS
        } else if (typeof define === 'function' && define.amd) {
            define(function () {
                return mainExports;
            });

            // <script>
        } else if (globalName) {
            this[globalName] = mainExports;
        }
    }

    // Override the current require with this new one
    parcelRequire = newRequire;

    if (error) {
        // throw error from earlier, _after updating parcelRequire_
        throw error;
    }

    return newRequire;
})(
    {
        DUgK: [
            function (require, module, exports) {
                'use strict';

                var __assign =
                    (this && this.__assign) ||
                    function () {
                        __assign =
                            Object.assign ||
                            function (t) {
                                for (
                                    var s, i = 1, n = arguments.length;
                                    i < n;
                                    i++
                                ) {
                                    s = arguments[i];
                                    for (var p in s)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                s,
                                                p
                                            )
                                        )
                                            t[p] = s[p];
                                }
                                return t;
                            };
                        return __assign.apply(this, arguments);
                    };
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.WidgetBase = void 0;
                var app_1 = require('./app');
                /// Base class for all widgets
                var WidgetBase = /** @class */ (function () {
                    function WidgetBase(elementId, state) {
                        this.elementId = elementId;
                        this.state = state;
                    }
                    Object.defineProperty(WidgetBase.prototype, 'element', {
                        /// Fetches the HTML element associated with this widget. This is a slow
                        /// operation and should be avoided if possible.
                        get: function get() {
                            var element = document.getElementById(
                                this.elementId
                            );
                            if (element === null) {
                                throw new Error(
                                    'Instance for element with id '.concat(
                                        this.elementId,
                                        ' cannot find its element'
                                    )
                                );
                            }
                            return element;
                        },
                        enumerable: false,
                        configurable: true,
                    });
                    /// Send a message to the python instance corresponding to this widget. The
                    /// message is an arbitrary JSON object and will be passed to the instance's
                    /// `_on_message` method.
                    WidgetBase.prototype.sendMessageToBackend = function (
                        message
                    ) {
                        (0, app_1.sendMessageOverWebsocket)({
                            type: 'widgetMessage',
                            // Remove the leading `reflex-id-` from the element's ID
                            widgetId: parseInt(this.elementId.substring(10)),
                            payload: message,
                        });
                    };
                    WidgetBase.prototype._setStateDontNotifyBackend = function (
                        deltaState
                    ) {
                        this.state = __assign(
                            __assign({}, this.state),
                            deltaState
                        );
                    };
                    WidgetBase.prototype.setStateAndNotifyBackend = function (
                        deltaState
                    ) {
                        this._setStateDontNotifyBackend(deltaState);
                        (0, app_1.sendMessageOverWebsocket)({
                            type: 'widgetStateUpdate',
                            // Remove the leading `reflex-id-` from the element's ID
                            widgetId: parseInt(this.elementId.substring(10)),
                            deltaState: deltaState,
                        });
                    };
                    return WidgetBase;
                })();
                exports.WidgetBase = WidgetBase;
                globalThis.WidgetBase = WidgetBase;
            },
            { './app': 'EVxB' },
        ],
        EmPY: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.TextWidget = void 0;
                var app_1 = require('./app');
                var widgetBase_1 = require('./widgetBase');
                var TextWidget = /** @class */ (function (_super) {
                    __extends(TextWidget, _super);
                    function TextWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    TextWidget.prototype.createElement = function () {
                        var element = document.createElement('div');
                        element.classList.add('reflex-text');
                        return element;
                    };
                    TextWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        if (deltaState.text !== undefined) {
                            element.innerText = deltaState.text;
                        }
                        if (deltaState.multiline !== undefined) {
                            element.style.whiteSpace = deltaState.multiline
                                ? 'normal'
                                : 'nowrap';
                        }
                        if (deltaState.style !== undefined) {
                            var style = deltaState.style;
                            element.style.fontFamily = style.fontName;
                            element.style.color = (0, app_1.colorToCss)(
                                style.fontColor
                            );
                            element.style.fontSize = style.fontSize + 'em';
                            element.style.fontStyle = style.italic
                                ? 'italic'
                                : 'normal';
                            element.style.fontWeight = style.fontWeight;
                            element.style.textDecoration = style.underlined
                                ? 'underline'
                                : 'none';
                            element.style.textTransform = style.allCaps
                                ? 'uppercase'
                                : 'none';
                        }
                    };
                    return TextWidget;
                })(widgetBase_1.WidgetBase);
                exports.TextWidget = TextWidget;
            },
            { './app': 'EVxB', './widgetBase': 'DUgK' },
        ],
        DCF0: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.RowWidget = void 0;
                var app_1 = require('./app');
                var widgetBase_1 = require('./widgetBase');
                var RowWidget = /** @class */ (function (_super) {
                    __extends(RowWidget, _super);
                    function RowWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    RowWidget.prototype.createElement = function () {
                        var element = document.createElement('div');
                        element.classList.add('reflex-row');
                        return element;
                    };
                    RowWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        (0, app_1.replaceChildren)(
                            element,
                            deltaState.children
                        );
                        if (deltaState.spacing !== undefined) {
                            element.style.gap = ''.concat(
                                deltaState.spacing,
                                'em'
                            );
                        }
                    };
                    return RowWidget;
                })(widgetBase_1.WidgetBase);
                exports.RowWidget = RowWidget;
            },
            { './app': 'EVxB', './widgetBase': 'DUgK' },
        ],
        FDPZ: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.ColumnWidget = void 0;
                var app_1 = require('./app');
                var widgetBase_1 = require('./widgetBase');
                var ColumnWidget = /** @class */ (function (_super) {
                    __extends(ColumnWidget, _super);
                    function ColumnWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    ColumnWidget.prototype.createElement = function () {
                        var element = document.createElement('div');
                        element.classList.add('reflex-column');
                        return element;
                    };
                    ColumnWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        (0, app_1.replaceChildren)(
                            element,
                            deltaState.children
                        );
                        if (deltaState.spacing !== undefined) {
                            element.style.gap = ''.concat(
                                deltaState.spacing,
                                'em'
                            );
                        }
                    };
                    return ColumnWidget;
                })(widgetBase_1.WidgetBase);
                exports.ColumnWidget = ColumnWidget;
            },
            { './app': 'EVxB', './widgetBase': 'DUgK' },
        ],
        aj59: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.DropdownWidget = void 0;
                var widgetBase_1 = require('./widgetBase');
                var DropdownWidget = /** @class */ (function (_super) {
                    __extends(DropdownWidget, _super);
                    function DropdownWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    DropdownWidget.prototype.createElement = function () {
                        var _this = this;
                        var element = document.createElement('select');
                        element.classList.add('reflex-dropdown');
                        element.addEventListener('input', function () {
                            _this.setStateAndNotifyBackend({
                                value: element.value,
                            });
                        });
                        return element;
                    };
                    DropdownWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        if (deltaState.optionNames !== undefined) {
                            element.innerHTML = '';
                            for (
                                var _i = 0, _a = deltaState.optionNames;
                                _i < _a.length;
                                _i++
                            ) {
                                var optionName = _a[_i];
                                var option = document.createElement('option');
                                option.value = optionName;
                                option.text = optionName;
                                element.appendChild(option);
                            }
                        }
                        if (
                            deltaState.selectedName !== undefined &&
                            deltaState.selectedName !== null
                        ) {
                            element.value = deltaState.selectedName;
                        }
                    };
                    return DropdownWidget;
                })(widgetBase_1.WidgetBase);
                exports.DropdownWidget = DropdownWidget;
            },
            { './widgetBase': 'DUgK' },
        ],
        u1gD: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.RectangleWidget = void 0;
                var app_1 = require('./app');
                var widgetBase_1 = require('./widgetBase');
                function setBoxStyleVariables(element, style, prefix, suffix) {
                    // Do nothing if no style was passed
                    if (style === undefined) {
                        return;
                    }
                    // Define a set of CSS variables which should be set. For now without the
                    // prefix
                    var variables = {};
                    if (style === null) {
                        variables = {
                            background: 'transparent',
                            'stroke-color': 'transparent',
                            'stroke-width': '0rem',
                            'corner-radius-top-left': '0rem',
                            'corner-radius-top-right': '0rem',
                            'corner-radius-bottom-right': '0rem',
                            'corner-radius-bottom-left': '0rem',
                            'shadow-color': 'transparent',
                            'shadow-radius': '0rem',
                            'shadow-offset-x': '0rem',
                            'shadow-offset-y': '0rem',
                        };
                    } else {
                        variables['background'] = (0, app_1.fillToCss)(
                            style.fill
                        );
                        variables['stroke-color'] = (0, app_1.colorToCss)(
                            style.strokeColor
                        );
                        variables['stroke-width'] = ''.concat(
                            style.strokeWidth,
                            'em'
                        );
                        variables['corner-radius-top-left'] = ''.concat(
                            style.cornerRadius[0],
                            'em'
                        );
                        variables['corner-radius-top-right'] = ''.concat(
                            style.cornerRadius[1],
                            'em'
                        );
                        variables['corner-radius-bottom-right'] = ''.concat(
                            style.cornerRadius[2],
                            'em'
                        );
                        variables['corner-radius-bottom-left'] = ''.concat(
                            style.cornerRadius[3],
                            'em'
                        );
                        variables['shadow-color'] = (0, app_1.colorToCss)(
                            style.shadowColor
                        );
                        variables['shadow-radius'] = ''.concat(
                            style.shadowRadius,
                            'em'
                        );
                        variables['shadow-offset-x'] = ''.concat(
                            style.shadowOffset[0],
                            'em'
                        );
                        variables['shadow-offset-y'] = ''.concat(
                            style.shadowOffset[1],
                            'em'
                        );
                    }
                    // Set the variables and add the prefix
                    for (
                        var _i = 0, _a = Object.entries(variables);
                        _i < _a.length;
                        _i++
                    ) {
                        var _b = _a[_i],
                            key = _b[0],
                            value = _b[1];
                        element.style.setProperty(
                            '--'.concat(prefix).concat(key).concat(suffix),
                            value
                        );
                    }
                }
                var RectangleWidget = /** @class */ (function (_super) {
                    __extends(RectangleWidget, _super);
                    function RectangleWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    RectangleWidget.prototype.createElement = function () {
                        var element = document.createElement('div');
                        element.classList.add('reflex-rectangle');
                        return element;
                    };
                    RectangleWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        (0, app_1.replaceOnlyChild)(element, deltaState.child);
                        setBoxStyleVariables(
                            element,
                            deltaState.style,
                            'rectangle-',
                            ''
                        );
                        if (deltaState.transition_time !== undefined) {
                            element.style.transitionDuration = ''.concat(
                                deltaState.transition_time,
                                's'
                            );
                        }
                        if (deltaState.hover_style === null) {
                            element.classList.remove('reflex-rectangle-hover');
                        } else if (deltaState.hover_style !== undefined) {
                            element.classList.add('reflex-rectangle-hover');
                            setBoxStyleVariables(
                                element,
                                deltaState.hover_style,
                                'rectangle-',
                                '-hover'
                            );
                        }
                    };
                    return RectangleWidget;
                })(widgetBase_1.WidgetBase);
                exports.RectangleWidget = RectangleWidget;
            },
            { './app': 'EVxB', './widgetBase': 'DUgK' },
        ],
        E2Q9: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.StackWidget = void 0;
                var app_1 = require('./app');
                var widgetBase_1 = require('./widgetBase');
                var StackWidget = /** @class */ (function (_super) {
                    __extends(StackWidget, _super);
                    function StackWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    StackWidget.prototype.createElement = function () {
                        var element = document.createElement('div');
                        element.classList.add('reflex-stack');
                        return element;
                    };
                    StackWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        if (deltaState.children !== undefined) {
                            (0, app_1.replaceChildren)(
                                element,
                                deltaState.children
                            );
                            var zIndex = 0;
                            for (
                                var _i = 0, _a = element.children;
                                _i < _a.length;
                                _i++
                            ) {
                                var child = _a[_i];
                                child.style.zIndex = ''.concat(zIndex);
                                zIndex += 1;
                            }
                        }
                    };
                    return StackWidget;
                })(widgetBase_1.WidgetBase);
                exports.StackWidget = StackWidget;
            },
            { './app': 'EVxB', './widgetBase': 'DUgK' },
        ],
        K1Om: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                var __assign =
                    (this && this.__assign) ||
                    function () {
                        __assign =
                            Object.assign ||
                            function (t) {
                                for (
                                    var s, i = 1, n = arguments.length;
                                    i < n;
                                    i++
                                ) {
                                    s = arguments[i];
                                    for (var p in s)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                s,
                                                p
                                            )
                                        )
                                            t[p] = s[p];
                                }
                                return t;
                            };
                        return __assign.apply(this, arguments);
                    };
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.MouseEventListenerWidget = void 0;
                var app_1 = require('./app');
                var widgetBase_1 = require('./widgetBase');
                function eventMouseButtonToString(event) {
                    return {
                        button: ['left', 'middle', 'right'][event.button],
                    };
                }
                function eventMousePositionToString(event) {
                    return {
                        x: event.clientX / app_1.pixelsPerEm,
                        y: event.clientY / app_1.pixelsPerEm,
                    };
                }
                var MouseEventListenerWidget = /** @class */ (function (
                    _super
                ) {
                    __extends(MouseEventListenerWidget, _super);
                    function MouseEventListenerWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    MouseEventListenerWidget.prototype.createElement =
                        function () {
                            var element = document.createElement('div');
                            element.classList.add(
                                'reflex-mouse-event-listener'
                            );
                            return element;
                        };
                    MouseEventListenerWidget.prototype.updateElement =
                        function (element, deltaState) {
                            var _this = this;
                            (0, app_1.replaceOnlyChild)(
                                element,
                                deltaState.child
                            );
                            if (deltaState.reportMouseDown) {
                                element.onmousedown = function (e) {
                                    _this.sendMessageToBackend(
                                        __assign(
                                            __assign(
                                                {
                                                    type: 'mouseDown',
                                                },
                                                eventMouseButtonToString(e)
                                            ),
                                            eventMousePositionToString(e)
                                        )
                                    );
                                };
                            } else {
                                element.onmousedown = null;
                            }
                            if (deltaState.reportMouseUp) {
                                element.onmouseup = function (e) {
                                    _this.sendMessageToBackend(
                                        __assign(
                                            __assign(
                                                {
                                                    type: 'mouseUp',
                                                },
                                                eventMouseButtonToString(e)
                                            ),
                                            eventMousePositionToString(e)
                                        )
                                    );
                                };
                            } else {
                                element.onmouseup = null;
                            }
                            if (deltaState.reportMouseMove) {
                                element.onmousemove = function (e) {
                                    _this.sendMessageToBackend(
                                        __assign(
                                            {
                                                type: 'mouseMove',
                                            },
                                            eventMousePositionToString(e)
                                        )
                                    );
                                };
                            } else {
                                element.onmousemove = null;
                            }
                            if (deltaState.reportMouseEnter) {
                                element.onmouseenter = function (e) {
                                    _this.sendMessageToBackend(
                                        __assign(
                                            {
                                                type: 'mouseEnter',
                                            },
                                            eventMousePositionToString(e)
                                        )
                                    );
                                };
                            } else {
                                element.onmouseenter = null;
                            }
                            if (deltaState.reportMouseLeave) {
                                element.onmouseleave = function (e) {
                                    _this.sendMessageToBackend(
                                        __assign(
                                            {
                                                type: 'mouseLeave',
                                            },
                                            eventMousePositionToString(e)
                                        )
                                    );
                                };
                            } else {
                                element.onmouseleave = null;
                            }
                        };
                    return MouseEventListenerWidget;
                })(widgetBase_1.WidgetBase);
                exports.MouseEventListenerWidget = MouseEventListenerWidget;
            },
            { './app': 'EVxB', './widgetBase': 'DUgK' },
        ],
        g2Fb: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.TextInputWidget = void 0;
                var widgetBase_1 = require('./widgetBase');
                var TextInputWidget = /** @class */ (function (_super) {
                    __extends(TextInputWidget, _super);
                    function TextInputWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    TextInputWidget.prototype.createElement = function () {
                        var _this = this;
                        var element = document.createElement('input');
                        element.classList.add('reflex-text-input');
                        element.addEventListener('input', function () {
                            _this.setStateAndNotifyBackend({
                                text: element.value,
                            });
                        });
                        return element;
                    };
                    TextInputWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        var cast_element = element;
                        if (deltaState.secret !== undefined) {
                            cast_element.type = deltaState.secret
                                ? 'password'
                                : 'text';
                        }
                        if (deltaState.text !== undefined) {
                            cast_element.value = deltaState.text;
                        }
                        if (deltaState.placeholder !== undefined) {
                            cast_element.placeholder = deltaState.placeholder;
                        }
                    };
                    return TextInputWidget;
                })(widgetBase_1.WidgetBase);
                exports.TextInputWidget = TextInputWidget;
            },
            { './widgetBase': 'DUgK' },
        ],
        When: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.PlaceholderWidget = void 0;
                var app_1 = require('./app');
                var widgetBase_1 = require('./widgetBase');
                var PlaceholderWidget = /** @class */ (function (_super) {
                    __extends(PlaceholderWidget, _super);
                    function PlaceholderWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    PlaceholderWidget.prototype.createElement = function () {
                        var element = document.createElement('div');
                        return element;
                    };
                    PlaceholderWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        (0, app_1.replaceOnlyChild)(
                            element,
                            deltaState._child_
                        );
                    };
                    return PlaceholderWidget;
                })(widgetBase_1.WidgetBase);
                exports.PlaceholderWidget = PlaceholderWidget;
            },
            { './app': 'EVxB', './widgetBase': 'DUgK' },
        ],
        RrmF: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.SwitchWidget = void 0;
                var widgetBase_1 = require('./widgetBase');
                var SwitchWidget = /** @class */ (function (_super) {
                    __extends(SwitchWidget, _super);
                    function SwitchWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    SwitchWidget.prototype.createElement = function () {
                        var _this = this;
                        var element = document.createElement('div');
                        element.classList.add('reflex-switch');
                        element.addEventListener('click', function () {
                            _this.setStateAndNotifyBackend({
                                is_on: element.textContent !== 'true',
                            });
                        });
                        return element;
                    };
                    SwitchWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        if (deltaState.is_on !== undefined) {
                            element.textContent = deltaState.is_on.toString();
                            element.style.backgroundColor = deltaState.is_on
                                ? 'green'
                                : 'red';
                        }
                    };
                    return SwitchWidget;
                })(widgetBase_1.WidgetBase);
                exports.SwitchWidget = SwitchWidget;
            },
            { './widgetBase': 'DUgK' },
        ],
        grfb: [
            function (require, module, exports) {
                'use strict';

                var __extends =
                    (this && this.__extends) ||
                    (function () {
                        var _extendStatics = function extendStatics(d, b) {
                            _extendStatics =
                                Object.setPrototypeOf ||
                                ({
                                    __proto__: [],
                                } instanceof Array &&
                                    function (d, b) {
                                        d.__proto__ = b;
                                    }) ||
                                function (d, b) {
                                    for (var p in b)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                b,
                                                p
                                            )
                                        )
                                            d[p] = b[p];
                                };
                            return _extendStatics(d, b);
                        };
                        return function (d, b) {
                            if (typeof b !== 'function' && b !== null)
                                throw new TypeError(
                                    'Class extends value ' +
                                        String(b) +
                                        ' is not a constructor or null'
                                );
                            _extendStatics(d, b);
                            function __() {
                                this.constructor = d;
                            }
                            d.prototype =
                                b === null
                                    ? Object.create(b)
                                    : ((__.prototype = b.prototype), new __());
                        };
                    })();
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.ProgressCircleWidget = void 0;
                var app_1 = require('./app');
                var widgetBase_1 = require('./widgetBase');
                var ProgressCircleWidget = /** @class */ (function (_super) {
                    __extends(ProgressCircleWidget, _super);
                    function ProgressCircleWidget() {
                        return (
                            (_super !== null &&
                                _super.apply(this, arguments)) ||
                            this
                        );
                    }
                    ProgressCircleWidget.prototype.createElement = function () {
                        var element = document.createElement('div');
                        return element;
                    };
                    ProgressCircleWidget.prototype.updateElement = function (
                        element,
                        deltaState
                    ) {
                        if (deltaState._size_ !== undefined) {
                            var size = deltaState._size_[0];
                            element.style.setProperty('--size', size + 'em');
                        }
                        if (deltaState.color !== undefined) {
                            element.style.setProperty(
                                '--color',
                                (0, app_1.colorToCss)(deltaState.color)
                            );
                        }
                        if (deltaState.progress === undefined) {
                        } else if (deltaState.progress === null) {
                            element.classList.add(
                                'reflex-progress-circle-no-progress'
                            );
                        } else {
                            console.log('TODO: implement progress spinner');
                        }
                    };
                    return ProgressCircleWidget;
                })(widgetBase_1.WidgetBase);
                exports.ProgressCircleWidget = ProgressCircleWidget;
            },
            { './app': 'EVxB', './widgetBase': 'DUgK' },
        ],
        EVxB: [
            function (require, module, exports) {
                'use strict';

                var __assign =
                    (this && this.__assign) ||
                    function () {
                        __assign =
                            Object.assign ||
                            function (t) {
                                for (
                                    var s, i = 1, n = arguments.length;
                                    i < n;
                                    i++
                                ) {
                                    s = arguments[i];
                                    for (var p in s)
                                        if (
                                            Object.prototype.hasOwnProperty.call(
                                                s,
                                                p
                                            )
                                        )
                                            t[p] = s[p];
                                }
                                return t;
                            };
                        return __assign.apply(this, arguments);
                    };
                Object.defineProperty(exports, '__esModule', {
                    value: true,
                });
                exports.sendMessageOverWebsocket =
                    exports.replaceChildren =
                    exports.replaceOnlyChild =
                    exports.fillToCss =
                    exports.colorToCss =
                    exports.pixelsPerEm =
                        void 0;
                var text_1 = require('./text');
                var row_1 = require('./row');
                var column_1 = require('./column');
                var dropdown_1 = require('./dropdown');
                var rectangle_1 = require('./rectangle');
                var stack_1 = require('./stack');
                var mouseEventListener_1 = require('./mouseEventListener');
                var textInput_1 = require('./textInput');
                var placeholder_1 = require('./placeholder');
                var switch_1 = require('./switch');
                var progressCircle_1 = require('./progressCircle');
                var sessionToken = '{session_token}';
                var initialMessages = '{initial_messages}';
                var socket = null;
                exports.pixelsPerEm = 16;
                var elementsToInstances = new WeakMap();
                function colorToCss(color) {
                    var r = color[0],
                        g = color[1],
                        b = color[2],
                        a = color[3];
                    return 'rgba('
                        .concat(r * 255, ', ')
                        .concat(g * 255, ', ')
                        .concat(b * 255, ', ')
                        .concat(a, ')');
                }
                exports.colorToCss = colorToCss;
                function fillToCss(fill) {
                    // Solid Color
                    if (fill.type === 'solid') {
                        return colorToCss(fill.color);
                    }
                    // Linear Gradient
                    if (fill.type === 'linearGradient') {
                        if (fill.stops.length == 1) {
                            return colorToCss(fill.stops[0][0]);
                        }
                        var stopStrings = [];
                        for (var i = 0; i < fill.stops.length; i++) {
                            var color = fill.stops[i][0];
                            var position = fill.stops[i][1];
                            stopStrings.push(
                                ''
                                    .concat(colorToCss(color), ' ')
                                    .concat(position * 100, '%')
                            );
                        }
                        return 'linear-gradient('
                            .concat(fill.angleDegrees, 'deg, ')
                            .concat(stopStrings.join(', '), ')');
                    }
                    // Image
                    if (fill.type === 'image') {
                        var cssUrl = "url('".concat(fill.imageUrl, "')");
                        if (fill.fillMode == 'fit') {
                            return ''.concat(
                                cssUrl,
                                ' center/contain no-repeat'
                            );
                        } else if (fill.fillMode == 'stretch') {
                            return ''.concat(cssUrl, ' top left / 100% 100%');
                        } else if (fill.fillMode == 'tile') {
                            return ''.concat(cssUrl, ' left top repeat');
                        } else if (fill.fillMode == 'zoom') {
                            return ''.concat(cssUrl, ' center/cover no-repeat');
                        } else {
                            // Invalid fill mode
                            // @ts-ignore
                            throw 'Invalid fill mode for image fill: '.concat(
                                fill.type
                            );
                        }
                    }
                    // Invalid fill type
                    // @ts-ignore
                    throw 'Invalid fill type: '.concat(fill.type);
                }
                exports.fillToCss = fillToCss;
                var widgetClasses = {
                    'Column-builtin': column_1.ColumnWidget,
                    'Dropdown-builtin': dropdown_1.DropdownWidget,
                    'MouseEventListener-builtin':
                        mouseEventListener_1.MouseEventListenerWidget,
                    'ProgressCircle-builtin':
                        progressCircle_1.ProgressCircleWidget,
                    'Rectangle-builtin': rectangle_1.RectangleWidget,
                    'Row-builtin': row_1.RowWidget,
                    'Stack-builtin': stack_1.StackWidget,
                    'Switch-builtin': switch_1.SwitchWidget,
                    'Text-builtin': text_1.TextWidget,
                    'TextInput-builtin': textInput_1.TextInputWidget,
                    Placeholder: placeholder_1.PlaceholderWidget,
                };
                globalThis.widgetClasses = widgetClasses;
                function processMessage(message) {
                    console.log('Received message: ', message);
                    if (message.type == 'updateWidgetStates') {
                        updateWidgetStates(
                            message.deltaStates,
                            message.rootWidgetId
                        );
                    } else if (message.type == 'evaluateJavascript') {
                        eval(message.javascriptSource);
                    } else if (message.type == 'requestFileUpload') {
                        requestFileUpload(message);
                    } else {
                        throw 'Encountered unknown message type: '.concat(
                            message
                        );
                    }
                }
                function updateWidgetStates(message, rootWidgetId) {
                    // Create a HTML element to hold all latent widgets, so they aren't
                    // garbage collected while updating the DOM.
                    var latentWidgets = document.createElement('div');
                    document.body.appendChild(latentWidgets);
                    latentWidgets.id = 'reflex-latent-widgets';
                    latentWidgets.style.display = 'none';
                    // Make sure all widgets mentioned in the message have a corresponding HTML
                    // element
                    for (var id in message) {
                        var deltaState = message[id];
                        var elementId = 'reflex-id-'.concat(id);
                        var element = document.getElementById(elementId);
                        // This is a reused element, nothing to do
                        if (element) {
                            continue;
                        }
                        // Get the class for this widget
                        var widgetClass = widgetClasses[deltaState._type_];
                        // Make sure the widget type is valid (Just helpful for debugging)
                        if (!widgetClass) {
                            throw 'Encountered unknown widget type: '.concat(
                                deltaState._type_
                            );
                        }
                        // Create an instance for this widget
                        var instance = new widgetClass(elementId, deltaState);
                        // Build the widget
                        element = instance.createElement();
                        // Add a unique ID to the widget
                        element.id = elementId;
                        // Add the common css class to the widget
                        element.classList.add('reflex-widget');
                        // Store the widget's class name in the element. Used for debugging.
                        element.setAttribute(
                            'dbg-py-class',
                            deltaState._python_type_
                        );
                        // Set the widget's key, if it has one. Used for debugging.
                        var key = deltaState['key'];
                        if (key !== undefined) {
                            element.setAttribute('dbg-key', ''.concat(key));
                        }
                        // Create a mapping from the element to the widget instance
                        elementsToInstances.set(element, instance);
                        // Keep the widget alive
                        latentWidgets.appendChild(element);
                    }
                    // Update all widgets mentioned in the message
                    for (var id in message) {
                        var deltaState = message[id];
                        var element = document.getElementById(
                            'reflex-id-' + id
                        );
                        if (!element) {
                            throw 'Failed to find widget with id '.concat(
                                id,
                                ', despite only just creating it!?'
                            );
                        }
                        // Perform updates common to all widgets
                        commonUpdate(element, deltaState);
                        // Perform updates specific to this widget type
                        var instance = elementsToInstances.get(element);
                        instance.updateElement(element, deltaState);
                        // Update the widget's state
                        instance.state = __assign(
                            __assign({}, instance.state),
                            deltaState
                        );
                    }
                    // Replace the root widget if requested
                    if (rootWidgetId !== null) {
                        var rootElement = document.getElementById(
                            'reflex-id-'.concat(rootWidgetId)
                        );
                        document.body.innerHTML = '';
                        document.body.appendChild(rootElement);
                    }
                    // Remove the latent widgets
                    latentWidgets.remove();
                }
                function commonUpdate(element, state) {
                    // Margins
                    if (state._margin_ !== undefined) {
                        var _a = state._margin_,
                            left = _a[0],
                            top = _a[1],
                            right = _a[2],
                            bottom = _a[3];
                        if (left === 0) {
                            element.style.removeProperty('margin-left');
                        } else {
                            element.style.marginLeft = ''.concat(left, 'em');
                        }
                        if (top === 0) {
                            element.style.removeProperty('margin-top');
                        } else {
                            element.style.marginTop = ''.concat(top, 'em');
                        }
                        if (right === 0) {
                            element.style.removeProperty('margin-right');
                        } else {
                            element.style.marginRight = ''.concat(right, 'em');
                        }
                        if (bottom === 0) {
                            element.style.removeProperty('margin-bottom');
                        } else {
                            element.style.marginBottom = ''.concat(
                                bottom,
                                'em'
                            );
                        }
                    }
                    // Alignment
                    if (state._align_ !== undefined) {
                        var _b = state._align_,
                            align_x = _b[0],
                            align_y = _b[1];
                        var transform_x = void 0;
                        if (align_x === null) {
                            element.style.removeProperty('left');
                            transform_x = 0;
                        } else {
                            element.style.left = ''.concat(align_x * 100, '%');
                            transform_x = align_x * -100;
                        }
                        var transform_y = void 0;
                        if (align_y === null) {
                            element.style.removeProperty('top');
                            transform_y = 0;
                        } else {
                            element.style.top = ''.concat(align_y * 100, '%');
                            transform_y = align_y * -100;
                        }
                        if (transform_x === 0 && transform_y === 0) {
                            element.style.removeProperty('transform');
                        } else {
                            element.style.transform = 'translate('
                                .concat(transform_x, '%, ')
                                .concat(transform_y, '%)');
                        }
                    }
                    // Width
                    //
                    // - If the width is set, use that
                    // - Widgets with an alignment don't grow, but use their natural size
                    // - Otherwise the widget's size is 100%. In this case however, margins must
                    //   be taken into account, since they aren't part of the `border-box`.
                    var newSize = state._size_
                        ? state._size_
                        : this.state._size_;
                    var newWidth = newSize[0],
                        newHeight = newSize[1];
                    var newAlign = state._align_
                        ? state._align_
                        : this.state._align_;
                    var newAlignX = newAlign[0],
                        newAlignY = newAlign[1];
                    var newMargins = state._margin_
                        ? state._margin_
                        : this.state._margin_;
                    var newMarginLeft = newMargins[0],
                        newMarginTop = newMargins[1],
                        newMarginRight = newMargins[2],
                        newMarginBottom = newMargins[3];
                    var newMarginX = newMarginLeft + newMarginRight;
                    var newMarginY = newMarginTop + newMarginBottom;
                    if (newWidth !== null) {
                        element.style.width = ''.concat(newWidth, 'em');
                    } else if (newAlignX !== null) {
                        element.style.width = 'max-content';
                    } else if (newMarginX !== 0) {
                        element.style.width = 'calc(100% - '.concat(
                            newMarginX,
                            'em)'
                        );
                    } else {
                        element.style.removeProperty('width');
                    }
                    if (newHeight != null) {
                        element.style.height = ''.concat(newHeight, 'em');
                    } else if (newAlignY !== null) {
                        element.style.height = 'max-content';
                    } else if (newMarginY !== 0) {
                        element.style.height = 'calc(100% - '.concat(
                            newMarginY,
                            'em)'
                        );
                    } else {
                        element.style.removeProperty('height');
                    }
                }
                function replaceOnlyChild(parentElement, childId) {
                    // If undefined, do nothing
                    if (childId === undefined) {
                        return;
                    }
                    // If null, remove the child
                    if (childId === null) {
                        parentElement.innerHTML = '';
                        return;
                    }
                    var currentChildElement = parentElement.firstElementChild;
                    // If a child already exists, either move it to the latent container or
                    // leave it alone if it's already the correct element
                    if (currentChildElement !== null) {
                        // Don't reparent the child if not necessary. This way things like
                        // keyboard focus are preserved
                        if (
                            currentChildElement.id ===
                            'reflex-id-'.concat(childId)
                        ) {
                            return;
                        }
                        // Move the child element to a latent container, so it isn't garbage
                        // collected
                        var latentWidgets = document.getElementById(
                            'reflex-latent-widgets'
                        );
                        latentWidgets === null || latentWidgets === void 0
                            ? void 0
                            : latentWidgets.appendChild(currentChildElement);
                    }
                    // Add the replacement widget
                    var newElement = document.getElementById(
                        'reflex-id-' + childId
                    );
                    if (!newElement) {
                        throw 'Failed to find replacement widget with id '.concat(
                            childId
                        );
                    }
                    parentElement === null || parentElement === void 0
                        ? void 0
                        : parentElement.appendChild(newElement);
                }
                exports.replaceOnlyChild = replaceOnlyChild;
                function replaceChildren(parentElement, childIds) {
                    // If undefined, do nothing
                    if (childIds === undefined) {
                        return;
                    }
                    var latentWidgets = document.getElementById(
                        'reflex-latent-widgets'
                    );
                    var curElement = parentElement.firstElementChild;
                    var curIdIndex = 0;
                    while (true) {
                        // If there are no more children in the DOM element, add the remaining
                        // children
                        if (curElement === null) {
                            while (curIdIndex < childIds.length) {
                                var curId_1 = childIds[curIdIndex];
                                var newElement_1 = document.getElementById(
                                    'reflex-id-' + curId_1
                                );
                                parentElement.appendChild(newElement_1);
                                curIdIndex++;
                            }
                            break;
                        }
                        // If there are no more children in the message, remove the remaining
                        // DOM children
                        if (curIdIndex >= childIds.length) {
                            while (curElement !== null) {
                                var nextElement = curElement.nextElementSibling;
                                latentWidgets.appendChild(curElement);
                                curElement = nextElement;
                            }
                            break;
                        }
                        // This element is the correct element, move on
                        var curId = childIds[curIdIndex];
                        if (curElement.id === 'reflex-id-' + curId) {
                            curElement = curElement.nextElementSibling;
                            curIdIndex++;
                            continue;
                        }
                        // This element is not the correct element, insert the correct one
                        // instead
                        var newElement = document.getElementById(
                            'reflex-id-' + curId
                        );
                        parentElement.insertBefore(newElement, curElement);
                        curIdIndex++;
                    }
                }
                exports.replaceChildren = replaceChildren;
                function requestFileUpload(message) {
                    // Create a file upload input element
                    var input = document.createElement('input');
                    input.type = 'file';
                    input.multiple = message.multiple;
                    if (message.fileExtensions !== null) {
                        input.accept = message.fileExtensions.join(',');
                    }
                    input.style.display = 'none';
                    function finish() {
                        // Remove the input element from the DOM
                        input.remove();
                        // Remove any event listeners
                        window.removeEventListener('focus', finish);
                        // Build a `FormData` object containing the files
                        var data = new FormData();
                        var ii = 0;
                        for (
                            var _i = 0, _a = input.files || [];
                            _i < _a.length;
                            _i++
                        ) {
                            var file = _a[_i];
                            ii += 1;
                            data.append('file_names', file.name);
                            data.append('file_types', file.type);
                            data.append('file_sizes', file.size.toString());
                            data.append('file_streams', file, file.name);
                        }
                        // FastAPI has trouble parsing empty form data. Append a dummy value so
                        // it's never empty
                        data.append('dummy', 'dummy');
                        // Upload the files
                        fetch(message.uploadUrl, {
                            method: 'PUT',
                            body: data,
                        });
                    }
                    // Listen for changes to the input
                    input.addEventListener('change', finish);
                    // Detect if the window gains focus. This means the file upload dialog was
                    // closed without selecting a file
                    window.addEventListener('focus', finish, {
                        once: true,
                    });
                    // Add the input element to the DOM
                    document.body.appendChild(input);
                    // Trigger the file upload
                    input.click();
                }
                function main() {
                    // Determine the browser's font size
                    var measure = document.createElement('div');
                    measure.style.height = '10em';
                    document.body.appendChild(measure);
                    exports.pixelsPerEm = measure.offsetHeight / 10;
                    document.body.removeChild(measure);
                    // Process initial messages
                    console.log(
                        'Processing '.concat(
                            initialMessages.length,
                            ' initial message(s)'
                        )
                    );
                    for (
                        var _i = 0, initialMessages_1 = initialMessages;
                        _i < initialMessages_1.length;
                        _i++
                    ) {
                        var message = initialMessages_1[_i];
                        processMessage(message);
                    }
                    // Connect to the websocket
                    var url = new URL(
                        '/reflex/ws?sessionToken='.concat(sessionToken),
                        window.location.href
                    );
                    url.protocol = url.protocol.replace('http', 'ws');
                    console.log('Connecting websocket to '.concat(url.href));
                    socket = new WebSocket(url.href);
                    socket.addEventListener('open', onOpen);
                    socket.addEventListener('message', onMessage);
                    socket.addEventListener('error', onError);
                    socket.addEventListener('close', onClose);
                }
                function onOpen() {
                    console.log('Connection opened');
                }
                function onMessage(event) {
                    // Parse the message JSON
                    var message = JSON.parse(event.data);
                    // Handle it
                    processMessage(message);
                }
                function onError(event) {
                    console.log('Error: '.concat(event.message));
                }
                function onClose(event) {
                    console.log('Connection closed: '.concat(event.reason));
                }
                function sendMessageOverWebsocket(message) {
                    if (!socket) {
                        console.log(
                            'Attempted to send message, but the websocket is not connected: '.concat(
                                message
                            )
                        );
                        return;
                    }
                    socket.send(JSON.stringify(message));
                }
                exports.sendMessageOverWebsocket = sendMessageOverWebsocket;
                main();
            },
            {
                './text': 'EmPY',
                './row': 'DCF0',
                './column': 'FDPZ',
                './dropdown': 'aj59',
                './rectangle': 'u1gD',
                './stack': 'E2Q9',
                './mouseEventListener': 'K1Om',
                './textInput': 'g2Fb',
                './placeholder': 'When',
                './switch': 'RrmF',
                './progressCircle': 'grfb',
            },
        ],
    },
    {},
    ['EVxB'],
    null
);
//# sourceMappingURL=/app.js.map
