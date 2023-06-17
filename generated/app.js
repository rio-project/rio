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
        var currentRequire = typeof parcelRequire === 'function' && parcelRequire;
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

        var err = new Error('Cannot find module \'' + name + '\'');
        err.code = 'MODULE_NOT_FOUND';
        throw err;
      }

      localRequire.resolve = resolve;
      localRequire.cache = {};

      var module = cache[name] = new newRequire.Module(name);

      modules[name][0].call(module.exports, localRequire, module, module.exports, this);
    }

    return cache[name].exports;

    function localRequire(x){
      return newRequire(localRequire.resolve(x));
    }

    function resolve(x){
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
    modules[id] = [function (require, module) {
      module.exports = exports;
    }, {}];
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
    if (typeof exports === "object" && typeof module !== "undefined") {
      module.exports = mainExports;

    // RequireJS
    } else if (typeof define === "function" && define.amd) {
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
})({"DUgK":[function(require,module,exports) {
"use strict";

var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.WidgetBase = void 0;
var app_1 = require("./app");
/// Base class for all widgets
var WidgetBase = /** @class */function () {
  function WidgetBase(outerElementId, state) {
    this.outerElementId = outerElementId;
    this.state = state;
  }
  Object.defineProperty(WidgetBase.prototype, "innerElement", {
    /// Fetches the HTML element associated with this widget. This is a slow
    /// operation and should be avoided if possible.
    get: function get() {
      return this.outerElement.firstElementChild;
    },
    enumerable: false,
    configurable: true
  });
  Object.defineProperty(WidgetBase.prototype, "outerElement", {
    get: function get() {
      var element = document.getElementById(this.outerElementId);
      if (element === null) {
        throw new Error("Instance for element with id ".concat(this.outerElementId, " cannot find its element"));
      }
      return element;
    },
    enumerable: false,
    configurable: true
  });
  /// Send a message to the python instance corresponding to this widget. The
  /// message is an arbitrary JSON object and will be passed to the instance's
  /// `_on_message` method.
  WidgetBase.prototype.sendMessageToBackend = function (message) {
    (0, app_1.sendMessageOverWebsocket)({
      type: 'widgetMessage',
      // Remove the leading `reflex-id-` from the element's ID
      widgetId: parseInt(this.outerElementId.substring(10)),
      payload: message
    });
  };
  WidgetBase.prototype._setStateDontNotifyBackend = function (deltaState) {
    // Set the state
    this.state = __assign(__assign({}, this.state), deltaState);
    // Trigger an update
    // @ts-ignore
    this.updateInnerElement(this.innerElement, deltaState);
  };
  WidgetBase.prototype.setStateAndNotifyBackend = function (deltaState) {
    // Set the state. This also updates the widget
    this._setStateDontNotifyBackend(deltaState);
    // Notify the backend
    (0, app_1.sendMessageOverWebsocket)({
      type: 'widgetStateUpdate',
      // Remove the leading `reflex-id-` from the element's ID
      widgetId: parseInt(this.outerElementId.substring(10)),
      deltaState: deltaState
    });
  };
  return WidgetBase;
}();
exports.WidgetBase = WidgetBase;
globalThis.WidgetBase = WidgetBase;
},{"./app":"EVxB"}],"EmPY":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.TextWidget = void 0;
var app_1 = require("./app");
var widgetBase_1 = require("./widgetBase");
var TextWidget = /** @class */function (_super) {
  __extends(TextWidget, _super);
  function TextWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  TextWidget.prototype.createInnerElement = function () {
    var containerElement = document.createElement('div');
    containerElement.classList.add('reflex-text');
    var textElement = document.createElement('div');
    containerElement.appendChild(textElement);
    return containerElement;
  };
  TextWidget.prototype.updateInnerElement = function (containerElement, deltaState) {
    var textElement = containerElement.firstElementChild;
    if (deltaState.text !== undefined) {
      textElement.innerText = deltaState.text;
    }
    if (deltaState.multiline !== undefined) {
      textElement.style.whiteSpace = deltaState.multiline ? 'normal' : 'nowrap';
    }
    if (deltaState.style !== undefined) {
      var style = deltaState.style;
      textElement.style.fontFamily = style.fontName;
      textElement.style.color = (0, app_1.colorToCss)(style.fontColor);
      textElement.style.fontSize = style.fontSize + 'em';
      textElement.style.fontStyle = style.italic ? 'italic' : 'normal';
      textElement.style.fontWeight = style.fontWeight;
      textElement.style.textDecoration = style.underlined ? 'underline' : 'none';
      textElement.style.textTransform = style.allCaps ? 'uppercase' : 'none';
    }
  };
  return TextWidget;
}(widgetBase_1.WidgetBase);
exports.TextWidget = TextWidget;
},{"./app":"EVxB","./widgetBase":"DUgK"}],"DCF0":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.RowWidget = void 0;
var app_1 = require("./app");
var widgetBase_1 = require("./widgetBase");
var RowWidget = /** @class */function (_super) {
  __extends(RowWidget, _super);
  function RowWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  RowWidget.prototype.createInnerElement = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-row');
    return element;
  };
  RowWidget.prototype.updateInnerElement = function (element, deltaState) {
    (0, app_1.replaceChildren)(element, deltaState.children);
    if (deltaState.spacing !== undefined) {
      element.style.gap = "".concat(deltaState.spacing, "em");
    }
  };
  return RowWidget;
}(widgetBase_1.WidgetBase);
exports.RowWidget = RowWidget;
},{"./app":"EVxB","./widgetBase":"DUgK"}],"FDPZ":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ColumnWidget = void 0;
var app_1 = require("./app");
var widgetBase_1 = require("./widgetBase");
var ColumnWidget = /** @class */function (_super) {
  __extends(ColumnWidget, _super);
  function ColumnWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  ColumnWidget.prototype.createInnerElement = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-column');
    return element;
  };
  ColumnWidget.prototype.updateInnerElement = function (element, deltaState) {
    (0, app_1.replaceChildren)(element, deltaState.children);
    if (deltaState.spacing !== undefined) {
      element.style.gap = "".concat(deltaState.spacing, "em");
    }
  };
  return ColumnWidget;
}(widgetBase_1.WidgetBase);
exports.ColumnWidget = ColumnWidget;
},{"./app":"EVxB","./widgetBase":"DUgK"}],"aj59":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.DropdownWidget = void 0;
var widgetBase_1 = require("./widgetBase");
var DropdownWidget = /** @class */function (_super) {
  __extends(DropdownWidget, _super);
  function DropdownWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  DropdownWidget.prototype.createInnerElement = function () {
    var _this = this;
    var element = document.createElement('select');
    element.classList.add('reflex-dropdown');
    element.addEventListener('input', function () {
      _this.sendMessageToBackend({
        name: element.value
      });
    });
    return element;
  };
  DropdownWidget.prototype.updateInnerElement = function (element, deltaState) {
    if (deltaState.optionNames !== undefined) {
      element.innerHTML = '';
      for (var _i = 0, _a = deltaState.optionNames; _i < _a.length; _i++) {
        var optionName = _a[_i];
        var option = document.createElement('option');
        option.value = optionName;
        option.text = optionName;
        element.appendChild(option);
      }
    }
    if (deltaState.selectedName !== undefined) {
      if (deltaState.selectedName === null) {
        element.selectedIndex = -1;
      } else {
        element.value = deltaState.selectedName;
      }
    }
  };
  return DropdownWidget;
}(widgetBase_1.WidgetBase);
exports.DropdownWidget = DropdownWidget;
},{"./widgetBase":"DUgK"}],"u1gD":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.RectangleWidget = void 0;
var app_1 = require("./app");
var widgetBase_1 = require("./widgetBase");
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
      'stroke-width': '0em',
      'corner-radius-top-left': '0em',
      'corner-radius-top-right': '0em',
      'corner-radius-bottom-right': '0em',
      'corner-radius-bottom-left': '0em',
      'shadow-color': 'transparent',
      'shadow-radius': '0em',
      'shadow-offset-x': '0em',
      'shadow-offset-y': '0em'
    };
  } else {
    variables['background'] = (0, app_1.fillToCss)(style.fill);
    variables['stroke-color'] = (0, app_1.colorToCss)(style.strokeColor);
    variables['stroke-width'] = "".concat(style.strokeWidth, "em");
    variables['corner-radius-top-left'] = "".concat(style.cornerRadius[0], "em");
    variables['corner-radius-top-right'] = "".concat(style.cornerRadius[1], "em");
    variables['corner-radius-bottom-right'] = "".concat(style.cornerRadius[2], "em");
    variables['corner-radius-bottom-left'] = "".concat(style.cornerRadius[3], "em");
    variables['shadow-color'] = (0, app_1.colorToCss)(style.shadowColor);
    variables['shadow-radius'] = "".concat(style.shadowRadius, "em");
    variables['shadow-offset-x'] = "".concat(style.shadowOffset[0], "em");
    variables['shadow-offset-y'] = "".concat(style.shadowOffset[1], "em");
  }
  // Set the variables and add the prefix
  for (var _i = 0, _a = Object.entries(variables); _i < _a.length; _i++) {
    var _b = _a[_i],
      key = _b[0],
      value = _b[1];
    element.style.setProperty("--".concat(prefix).concat(key).concat(suffix), value);
  }
}
var RectangleWidget = /** @class */function (_super) {
  __extends(RectangleWidget, _super);
  function RectangleWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  RectangleWidget.prototype.createInnerElement = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-rectangle');
    return element;
  };
  RectangleWidget.prototype.updateInnerElement = function (element, deltaState) {
    (0, app_1.replaceOnlyChild)(element, deltaState.child);
    setBoxStyleVariables(element, deltaState.style, 'rectangle-', '');
    if (deltaState.transition_time !== undefined) {
      element.style.transitionDuration = "".concat(deltaState.transition_time, "s");
    }
    if (deltaState.hover_style === null) {
      element.classList.remove('reflex-rectangle-hover');
    } else if (deltaState.hover_style !== undefined) {
      element.classList.add('reflex-rectangle-hover');
      setBoxStyleVariables(element, deltaState.hover_style, 'rectangle-', '-hover');
    }
    if (deltaState.cursor !== undefined) {
      if (deltaState.cursor === 'default') {
        element.style.removeProperty('cursor');
      } else {
        element.style.cursor = deltaState.cursor;
      }
    }
  };
  return RectangleWidget;
}(widgetBase_1.WidgetBase);
exports.RectangleWidget = RectangleWidget;
},{"./app":"EVxB","./widgetBase":"DUgK"}],"E2Q9":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.StackWidget = void 0;
var app_1 = require("./app");
var widgetBase_1 = require("./widgetBase");
var StackWidget = /** @class */function (_super) {
  __extends(StackWidget, _super);
  function StackWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  StackWidget.prototype.createInnerElement = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-stack');
    return element;
  };
  StackWidget.prototype.updateInnerElement = function (element, deltaState) {
    if (deltaState.children !== undefined) {
      (0, app_1.replaceChildren)(element, deltaState.children);
      var zIndex = 0;
      for (var _i = 0, _a = element.children; _i < _a.length; _i++) {
        var child = _a[_i];
        child.style.zIndex = "".concat(zIndex);
        zIndex += 1;
      }
    }
  };
  return StackWidget;
}(widgetBase_1.WidgetBase);
exports.StackWidget = StackWidget;
},{"./app":"EVxB","./widgetBase":"DUgK"}],"K1Om":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.MouseEventListenerWidget = void 0;
var app_1 = require("./app");
var widgetBase_1 = require("./widgetBase");
function eventMouseButtonToString(event) {
  return {
    button: ['left', 'middle', 'right'][event.button]
  };
}
function eventMousePositionToString(event) {
  return {
    x: event.clientX / app_1.pixelsPerEm,
    y: event.clientY / app_1.pixelsPerEm
  };
}
var MouseEventListenerWidget = /** @class */function (_super) {
  __extends(MouseEventListenerWidget, _super);
  function MouseEventListenerWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  MouseEventListenerWidget.prototype.createInnerElement = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-mouse-event-listener');
    return element;
  };
  MouseEventListenerWidget.prototype.updateInnerElement = function (element, deltaState) {
    var _this = this;
    (0, app_1.replaceOnlyChild)(element, deltaState.child);
    if (deltaState.reportMouseDown) {
      element.onmousedown = function (e) {
        _this.sendMessageToBackend(__assign(__assign({
          type: 'mouseDown'
        }, eventMouseButtonToString(e)), eventMousePositionToString(e)));
      };
    } else {
      element.onmousedown = null;
    }
    if (deltaState.reportMouseUp) {
      element.onmouseup = function (e) {
        _this.sendMessageToBackend(__assign(__assign({
          type: 'mouseUp'
        }, eventMouseButtonToString(e)), eventMousePositionToString(e)));
      };
    } else {
      element.onmouseup = null;
    }
    if (deltaState.reportMouseMove) {
      element.onmousemove = function (e) {
        _this.sendMessageToBackend(__assign({
          type: 'mouseMove'
        }, eventMousePositionToString(e)));
      };
    } else {
      element.onmousemove = null;
    }
    if (deltaState.reportMouseEnter) {
      element.onmouseenter = function (e) {
        _this.sendMessageToBackend(__assign({
          type: 'mouseEnter'
        }, eventMousePositionToString(e)));
      };
    } else {
      element.onmouseenter = null;
    }
    if (deltaState.reportMouseLeave) {
      element.onmouseleave = function (e) {
        _this.sendMessageToBackend(__assign({
          type: 'mouseLeave'
        }, eventMousePositionToString(e)));
      };
    } else {
      element.onmouseleave = null;
    }
  };
  return MouseEventListenerWidget;
}(widgetBase_1.WidgetBase);
exports.MouseEventListenerWidget = MouseEventListenerWidget;
},{"./app":"EVxB","./widgetBase":"DUgK"}],"g2Fb":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.TextInputWidget = void 0;
var widgetBase_1 = require("./widgetBase");
var TextInputWidget = /** @class */function (_super) {
  __extends(TextInputWidget, _super);
  function TextInputWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  TextInputWidget.prototype.createInnerElement = function () {
    var _this = this;
    var element = document.createElement('input');
    element.classList.add('reflex-text-input');
    // Detect value changes and send them to the backend
    element.addEventListener('blur', function () {
      _this.setStateAndNotifyBackend({
        text: element.value
      });
    });
    // Detect the enter key and send it to the backend
    //
    // In addition to notifying the backend, also include the input's
    // current value. This ensures any event handlers actually use the up-to
    // date value.
    element.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        _this.sendMessageToBackend({
          text: element.value
        });
      }
    });
    return element;
  };
  TextInputWidget.prototype.updateInnerElement = function (element, deltaState) {
    var cast_element = element;
    if (deltaState.secret !== undefined) {
      cast_element.type = deltaState.secret ? 'password' : 'text';
    }
    if (deltaState.text !== undefined) {
      cast_element.value = deltaState.text;
    }
    if (deltaState.placeholder !== undefined) {
      cast_element.placeholder = deltaState.placeholder;
    }
  };
  return TextInputWidget;
}(widgetBase_1.WidgetBase);
exports.TextInputWidget = TextInputWidget;
},{"./widgetBase":"DUgK"}],"When":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.PlaceholderWidget = void 0;
var app_1 = require("./app");
var widgetBase_1 = require("./widgetBase");
var PlaceholderWidget = /** @class */function (_super) {
  __extends(PlaceholderWidget, _super);
  function PlaceholderWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  PlaceholderWidget.prototype.createInnerElement = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-placeholder');
    return element;
  };
  PlaceholderWidget.prototype.updateInnerElement = function (element, deltaState) {
    (0, app_1.replaceOnlyChild)(element, deltaState._child_);
  };
  return PlaceholderWidget;
}(widgetBase_1.WidgetBase);
exports.PlaceholderWidget = PlaceholderWidget;
},{"./app":"EVxB","./widgetBase":"DUgK"}],"RrmF":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.SwitchWidget = void 0;
var app_1 = require("./app");
var widgetBase_1 = require("./widgetBase");
var SwitchWidget = /** @class */function (_super) {
  __extends(SwitchWidget, _super);
  function SwitchWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  SwitchWidget.prototype.createInnerElement = function () {
    var _this = this;
    var element = document.createElement('div');
    element.classList.add('reflex-switch');
    var containerElement = document.createElement('div');
    containerElement.classList.add('container');
    element.appendChild(containerElement);
    var checkboxElement = document.createElement('input');
    checkboxElement.type = 'checkbox';
    containerElement.appendChild(checkboxElement);
    var knobElement = document.createElement('div');
    knobElement.classList.add('knob');
    containerElement.appendChild(knobElement);
    checkboxElement.addEventListener('change', function () {
      _this.setStateAndNotifyBackend({
        is_on: checkboxElement.checked
      });
    });
    return element;
  };
  SwitchWidget.prototype.updateInnerElement = function (element, deltaState) {
    if (deltaState.is_on !== undefined) {
      if (deltaState.is_on) {
        element.classList.add('is-on');
      } else {
        element.classList.remove('is-on');
      }
      // Assign the new value to the checkbox element, but only if it
      // differs from the current value, to avoid immediately triggering
      // the event again.
      var checkboxElement = element.querySelector('input');
      if ((checkboxElement === null || checkboxElement === void 0 ? void 0 : checkboxElement.checked) !== deltaState.is_on) {
        checkboxElement.checked = deltaState.is_on;
      }
    }
    if (deltaState.knobColorOff !== undefined) {
      element.style.setProperty('--switch-knob-color-off', (0, app_1.colorToCss)(deltaState.knobColorOff));
    }
    if (deltaState.knobColorOn !== undefined) {
      element.style.setProperty('--switch-knob-color-on', (0, app_1.colorToCss)(deltaState.knobColorOn));
    }
    if (deltaState.backgroundColorOff !== undefined) {
      element.style.setProperty('--switch-background-color-off', (0, app_1.colorToCss)(deltaState.backgroundColorOff));
    }
    if (deltaState.backgroundColorOn !== undefined) {
      element.style.setProperty('--switch-background-color-on', (0, app_1.colorToCss)(deltaState.backgroundColorOn));
    }
  };
  return SwitchWidget;
}(widgetBase_1.WidgetBase);
exports.SwitchWidget = SwitchWidget;
},{"./app":"EVxB","./widgetBase":"DUgK"}],"grfb":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ProgressCircleWidget = void 0;
var app_1 = require("./app");
var widgetBase_1 = require("./widgetBase");
var ProgressCircleWidget = /** @class */function (_super) {
  __extends(ProgressCircleWidget, _super);
  function ProgressCircleWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  ProgressCircleWidget.prototype.createInnerElement = function () {
    var element = document.createElement('div');
    element.innerHTML = "\n            <svg viewBox=\"25 25 50 50\">\n                <circle class=\"background\" cx=\"50\" cy=\"50\" r=\"20\"></circle>\n                <circle class=\"progress\" cx=\"50\" cy=\"50\" r=\"20\"></circle>\n            </svg>\n        ";
    element.classList.add('reflex-progress-circle');
    return element;
  };
  ProgressCircleWidget.prototype.updateInnerElement = function (element, deltaState) {
    if (deltaState.color !== undefined) {
      element.style.stroke = (0, app_1.colorToCss)(deltaState.color);
    }
    if (deltaState.background_color !== undefined) {
      element.style.setProperty('--background-color', (0, app_1.colorToCss)(deltaState.background_color));
    }
    if (deltaState.progress !== undefined) {
      if (deltaState.progress === null) {
        element.classList.add('spinning');
      } else {
        element.classList.remove('spinning');
        var fullCircle = 40 * Math.PI;
        element.style.setProperty('--dasharray', "".concat(deltaState.progress * fullCircle, ", ").concat((1 - deltaState.progress) * fullCircle));
      }
    }
  };
  return ProgressCircleWidget;
}(widgetBase_1.WidgetBase);
exports.ProgressCircleWidget = ProgressCircleWidget;
},{"./app":"EVxB","./widgetBase":"DUgK"}],"NWKb":[function(require,module,exports) {
"use strict";

var __extends = this && this.__extends || function () {
  var _extendStatics = function extendStatics(d, b) {
    _extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return _extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    _extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.PlotWidget = void 0;
var widgetBase_1 = require("./widgetBase");
function loadPlotly(callback) {
  if (typeof Plotly === 'undefined') {
    console.log('Fetching plotly.js');
    var script = document.createElement('script');
    script.src = '/reflex/asset/plotly.min.js';
    script.onload = callback;
    document.head.appendChild(script);
  } else {
    callback();
  }
}
var PlotWidget = /** @class */function (_super) {
  __extends(PlotWidget, _super);
  function PlotWidget() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  PlotWidget.prototype.createInnerElement = function () {
    var element = document.createElement('div');
    element.style.display = 'inline-block';
    return element;
  };
  PlotWidget.prototype.updateInnerElement = function (element, deltaState) {
    if (deltaState.plotJson !== undefined) {
      element.innerHTML = '';
      loadPlotly(function () {
        var plotJson = JSON.parse(deltaState.plotJson);
        Plotly.newPlot(element, plotJson.data, plotJson.layout, {
          responsive: true
        });
      });
    }
  };
  return PlotWidget;
}(widgetBase_1.WidgetBase);
exports.PlotWidget = PlotWidget;
},{"./widgetBase":"DUgK"}],"EVxB":[function(require,module,exports) {
"use strict";

var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.sendMessageOverWebsocket = exports.replaceChildren = exports.replaceOnlyChild = exports.fillToCss = exports.colorToCss = exports.pixelsPerEm = void 0;
var text_1 = require("./text");
var row_1 = require("./row");
var column_1 = require("./column");
var dropdown_1 = require("./dropdown");
var rectangle_1 = require("./rectangle");
var stack_1 = require("./stack");
var mouseEventListener_1 = require("./mouseEventListener");
var textInput_1 = require("./textInput");
var placeholder_1 = require("./placeholder");
var switch_1 = require("./switch");
var progressCircle_1 = require("./progressCircle");
var plot_1 = require("./plot");
var sessionToken = '{session_token}';
var initialMessages = '{initial_messages}';
var socket = null;
exports.pixelsPerEm = 16;
var outerElementsToInstances = new WeakMap();
function colorToCss(color) {
  var r = color[0],
    g = color[1],
    b = color[2],
    a = color[3];
  return "rgba(".concat(r * 255, ", ").concat(g * 255, ", ").concat(b * 255, ", ").concat(a, ")");
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
      stopStrings.push("".concat(colorToCss(color), " ").concat(position * 100, "%"));
    }
    return "linear-gradient(".concat(fill.angleDegrees, "deg, ").concat(stopStrings.join(', '), ")");
  }
  // Image
  if (fill.type === 'image') {
    var cssUrl = "url('".concat(fill.imageUrl, "')");
    if (fill.fillMode == 'fit') {
      return "".concat(cssUrl, " center/contain no-repeat");
    } else if (fill.fillMode == 'stretch') {
      return "".concat(cssUrl, " top left / 100% 100%");
    } else if (fill.fillMode == 'tile') {
      return "".concat(cssUrl, " left top repeat");
    } else if (fill.fillMode == 'zoom') {
      return "".concat(cssUrl, " center/cover no-repeat");
    } else {
      // Invalid fill mode
      // @ts-ignore
      throw "Invalid fill mode for image fill: ".concat(fill.type);
    }
  }
  // Invalid fill type
  // @ts-ignore
  throw "Invalid fill type: ".concat(fill.type);
}
exports.fillToCss = fillToCss;
var widgetClasses = {
  'Column-builtin': column_1.ColumnWidget,
  'Dropdown-builtin': dropdown_1.DropdownWidget,
  'MouseEventListener-builtin': mouseEventListener_1.MouseEventListenerWidget,
  'Plot-builtin': plot_1.PlotWidget,
  'ProgressCircle-builtin': progressCircle_1.ProgressCircleWidget,
  'Rectangle-builtin': rectangle_1.RectangleWidget,
  'Row-builtin': row_1.RowWidget,
  'Stack-builtin': stack_1.StackWidget,
  'Switch-builtin': switch_1.SwitchWidget,
  'Text-builtin': text_1.TextWidget,
  'TextInput-builtin': textInput_1.TextInputWidget,
  Placeholder: placeholder_1.PlaceholderWidget
};
globalThis.widgetClasses = widgetClasses;
function processMessage(message) {
  console.log('Received message: ', message);
  if (message.type == 'updateWidgetStates') {
    updateWidgetStates(message.deltaStates, message.rootWidgetId);
  } else if (message.type == 'evaluateJavascript') {
    eval(message.javascriptSource);
  } else if (message.type == 'requestFileUpload') {
    requestFileUpload(message);
  } else {
    throw "Encountered unknown message type: ".concat(message);
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
    var elementId = "reflex-id-".concat(id);
    var outerElement = document.getElementById(elementId);
    // This is a reused element, nothing to do
    if (outerElement) {
      continue;
    }
    // Get the class for this widget
    var widgetClass = widgetClasses[deltaState._type_];
    // Make sure the widget type is valid (Just helpful for debugging)
    if (!widgetClass) {
      throw "Encountered unknown widget type: ".concat(deltaState._type_);
    }
    // Create an instance for this widget
    var instance = new widgetClass(elementId, deltaState);
    // Build the widget
    outerElement = document.createElement('div');
    var innerElement = instance.createInnerElement();
    outerElement.appendChild(innerElement);
    // Add a unique ID to the widget
    outerElement.id = elementId;
    // Add the common css class to the widget
    innerElement.classList.add('reflex-inner');
    outerElement.classList.add('reflex-outer');
    // Store the widget's class name in the element. Used for debugging.
    outerElement.setAttribute('dbg-py-class', deltaState._python_type_);
    // Set the widget's key, if it has one. Used for debugging.
    var key = deltaState['key'];
    if (key !== undefined) {
      outerElement.setAttribute('dbg-key', "".concat(key));
    }
    // Create a mapping from the element to the widget instance
    outerElementsToInstances.set(outerElement, instance);
    // Keep the widget alive
    latentWidgets.appendChild(outerElement);
  }
  // Update all widgets mentioned in the message
  var widgetsNeedingGrowUpdate = new Set();
  for (var id in message) {
    var deltaState = message[id];
    var outerElement = document.getElementById('reflex-id-' + id);
    var innerElement = outerElement.firstChild;
    if (!outerElement) {
      throw "Failed to find widget with id ".concat(id, ", despite only just creating it!?");
    }
    // Perform updates common to all widgets
    commonUpdate(outerElement, innerElement, deltaState);
    // Perform updates specific to this widget type
    var instance = outerElementsToInstances.get(outerElement);
    instance.updateInnerElement(innerElement, deltaState);
    // Update the widget's state
    instance.state = __assign(__assign({}, instance.state), deltaState);
    // Mark the widget and its children as needing a flex-grow update
    widgetsNeedingGrowUpdate.add(instance);
    for (var _i = 0, _a = outerElement.childNodes; _i < _a.length; _i++) {
      var childElement = _a[_i];
      var childInstance = outerElementsToInstances.get(childElement);
      if (childInstance !== undefined) {
        widgetsNeedingGrowUpdate.add(childInstance);
      }
    }
  }
  // Update each element's `flex-grow`. This can only be done after all
  // widgets have their correct parent set.
  widgetsNeedingGrowUpdate.forEach(updateFlexGrow);
  // Replace the root widget if requested
  if (rootWidgetId !== null) {
    var rootElement = document.getElementById("reflex-id-".concat(rootWidgetId));
    document.body.innerHTML = '';
    document.body.appendChild(rootElement);
  }
  // Remove the latent widgets
  latentWidgets.remove();
}
function commonUpdate(outerElement, innerElement, state) {
  // Margins
  if (state._margin_ !== undefined) {
    var _a = state._margin_,
      left = _a[0],
      top = _a[1],
      right = _a[2],
      bottom = _a[3];
    if (left === 0) {
      innerElement.style.removeProperty('margin-left');
    } else {
      innerElement.style.marginLeft = "".concat(left, "em");
    }
    if (top === 0) {
      innerElement.style.removeProperty('margin-top');
    } else {
      innerElement.style.marginTop = "".concat(top, "em");
    }
    if (right === 0) {
      innerElement.style.removeProperty('margin-right');
    } else {
      innerElement.style.marginRight = "".concat(right, "em");
    }
    if (bottom === 0) {
      innerElement.style.removeProperty('margin-bottom');
    } else {
      innerElement.style.marginBottom = "".concat(bottom, "em");
    }
  }
  // Alignment
  if (state._align_ !== undefined) {
    var _b = state._align_,
      align_x = _b[0],
      align_y = _b[1];
    var transform_x = void 0;
    if (align_x === null) {
      innerElement.style.removeProperty('left');
      transform_x = 0;
    } else {
      innerElement.style.left = "".concat(align_x * 100, "%");
      transform_x = align_x * -100;
    }
    var transform_y = void 0;
    if (align_y === null) {
      innerElement.style.removeProperty('top');
      transform_y = 0;
    } else {
      innerElement.style.top = "".concat(align_y * 100, "%");
      transform_y = align_y * -100;
    }
    if (transform_x === 0 && transform_y === 0) {
      innerElement.style.removeProperty('transform');
    } else {
      innerElement.style.transform = "translate(".concat(transform_x, "%, ").concat(transform_y, "%)");
    }
  }
  // Width
  //
  // - If the width is set, use that
  // - Widgets with an alignment don't grow, but use their natural size
  // - Otherwise the widget's size is 100%. In this case however, margins must
  //   be taken into account, since they aren't part of the `border-box`.
  var newSize = state._size_ ? state._size_ : this.state._size_;
  var newWidth = newSize[0],
    newHeight = newSize[1];
  var newAlign = state._align_ ? state._align_ : this.state._align_;
  var newAlignX = newAlign[0],
    newAlignY = newAlign[1];
  var newMargins = state._margin_ ? state._margin_ : this.state._margin_;
  var newMarginLeft = newMargins[0],
    newMarginTop = newMargins[1],
    newMarginRight = newMargins[2],
    newMarginBottom = newMargins[3];
  var newMarginX = newMarginLeft + newMarginRight;
  var newMarginY = newMarginTop + newMarginBottom;
  if (newWidth !== null) {
    innerElement.style.minWidth = "".concat(newWidth, "em");
  } else if (newAlignX !== null) {
    innerElement.style.minWidth = 'max-content';
  } else if (newMarginX !== 0) {
    innerElement.style.minWidth = "calc(100% - ".concat(newMarginX, "em)");
  } else {
    innerElement.style.removeProperty('min-width');
  }
  if (newHeight != null) {
    innerElement.style.minHeight = "".concat(newHeight, "em");
  } else if (newAlignY !== null) {
    innerElement.style.minHeight = 'max-content';
  } else if (newMarginY !== 0) {
    innerElement.style.minHeight = "calc(100% - ".concat(newMarginY, "em)");
  } else {
    innerElement.style.removeProperty('min-height');
  }
}
function updateFlexGrow(widget) {
  // Is the parent horizontally or vertically oriented?
  var outerElement = widget.outerElement;
  var parentFlexDirection = getComputedStyle(outerElement.parentElement).flexDirection;
  var isParentHorizontal = parentFlexDirection !== 'column';
  // Get this widget's relevant property
  var grow;
  if (isParentHorizontal) {
    grow = widget.state['_grow_'][0];
  } else {
    grow = widget.state['_grow_'][1];
  }
  // If the size is overridden, don't grow
  if (grow) {
    outerElement.style.removeProperty('flex-grow');
  } else {
    outerElement.style.flexGrow = '0';
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
    if (currentChildElement.id === "reflex-id-".concat(childId)) {
      return;
    }
    // Move the child element to a latent container, so it isn't garbage
    // collected
    var latentWidgets = document.getElementById('reflex-latent-widgets');
    latentWidgets === null || latentWidgets === void 0 ? void 0 : latentWidgets.appendChild(currentChildElement);
  }
  // Add the replacement widget
  var newElement = document.getElementById('reflex-id-' + childId);
  if (!newElement) {
    throw "Failed to find replacement widget with id ".concat(childId);
  }
  parentElement === null || parentElement === void 0 ? void 0 : parentElement.appendChild(newElement);
}
exports.replaceOnlyChild = replaceOnlyChild;
function replaceChildren(parentElement, childIds) {
  // If undefined, do nothing
  if (childIds === undefined) {
    return;
  }
  var latentWidgets = document.getElementById('reflex-latent-widgets');
  var curElement = parentElement.firstElementChild;
  var curIdIndex = 0;
  while (true) {
    // If there are no more children in the DOM element, add the remaining
    // children
    if (curElement === null) {
      while (curIdIndex < childIds.length) {
        var curId_1 = childIds[curIdIndex];
        var newElement_1 = document.getElementById('reflex-id-' + curId_1);
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
    var newElement = document.getElementById('reflex-id-' + curId);
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
    // Don't run twice
    if (input.parentElement === null) {
      return;
    }
    // Build a `FormData` object containing the files
    var data = new FormData();
    var ii = 0;
    for (var _i = 0, _a = input.files || []; _i < _a.length; _i++) {
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
      body: data
    });
    // Remove the input element from the DOM. Removing this too early causes
    // weird behavior in some browsers
    input.remove();
  }
  // Listen for changes to the input
  input.addEventListener('change', finish);
  // Detect if the window gains focus. This means the file upload dialog was
  // closed without selecting a file
  window.addEventListener('focus', function () {
    // In some browsers `focus` fires before `change`. Give `change`
    // time to run first.
    this.window.setTimeout(finish, 500);
  }, {
    once: true
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
  console.log("Processing ".concat(initialMessages.length, " initial message(s)"));
  for (var _i = 0, initialMessages_1 = initialMessages; _i < initialMessages_1.length; _i++) {
    var message = initialMessages_1[_i];
    processMessage(message);
  }
  // Connect to the websocket
  var url = new URL("/reflex/ws?sessionToken=".concat(sessionToken), window.location.href);
  url.protocol = url.protocol.replace('http', 'ws');
  console.log("Connecting websocket to ".concat(url.href));
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
  console.log("Error: ".concat(event.message));
}
function onClose(event) {
  console.log("Connection closed: ".concat(event.reason));
}
function sendMessageOverWebsocket(message) {
  if (!socket) {
    console.log("Attempted to send message, but the websocket is not connected: ".concat(message));
    return;
  }
  console.log('Sending message: ', message);
  socket.send(JSON.stringify(message));
}
exports.sendMessageOverWebsocket = sendMessageOverWebsocket;
main();
},{"./text":"EmPY","./row":"DCF0","./column":"FDPZ","./dropdown":"aj59","./rectangle":"u1gD","./stack":"E2Q9","./mouseEventListener":"K1Om","./textInput":"g2Fb","./placeholder":"When","./switch":"RrmF","./progressCircle":"grfb","./plot":"NWKb"}]},{},["EVxB"], null)
//# sourceMappingURL=/app.js.map