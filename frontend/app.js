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
})({"EmPY":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.TextWidget = void 0;
var app_1 = require("./app");
var TextWidget = /** @class */function () {
  function TextWidget() {}
  TextWidget.build = function (data) {
    var element = document.createElement('div');
    return element;
  };
  TextWidget.update = function (element, deltaState) {
    if (deltaState.text !== undefined) {
      element.innerText = deltaState.text;
    }
    if (deltaState.multiline !== undefined) {
      element.style.whiteSpace = deltaState.multiline ? 'normal' : 'nowrap';
    }
    if (deltaState.font !== undefined) {
      element.style.fontFamily = deltaState.font;
    }
    if (deltaState.font_color !== undefined) {
      element.style.color = (0, app_1.colorToCss)(deltaState.font_color);
    }
    if (deltaState.font_size !== undefined) {
      element.style.fontSize = deltaState.font_size + 'em';
    }
    if (deltaState.font_weight !== undefined) {
      element.style.fontWeight = deltaState.font_weight;
    }
    if (deltaState.italic !== undefined) {
      element.style.fontStyle = deltaState.italic ? 'italic' : 'normal';
    }
    if (deltaState.underlined !== undefined) {
      element.style.textDecoration = deltaState.underlined ? 'underline' : 'none';
    }
  };
  return TextWidget;
}();
exports.TextWidget = TextWidget;
},{"./app":"EVxB"}],"DCF0":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.RowWidget = void 0;
var app_1 = require("./app");
var RowWidget = /** @class */function () {
  function RowWidget() {}
  RowWidget.build = function (data) {
    var element = document.createElement('div');
    element.classList.add('pygui-row');
    for (var _i = 0, _a = data.children; _i < _a.length; _i++) {
      var child = _a[_i];
      element.appendChild((0, app_1.buildWidget)(child));
    }
    return element;
  };
  RowWidget.update = function (element, deltaState) {};
  return RowWidget;
}();
exports.RowWidget = RowWidget;
},{"./app":"EVxB"}],"FDPZ":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ColumnWidget = void 0;
var app_1 = require("./app");
var ColumnWidget = /** @class */function () {
  function ColumnWidget() {}
  ColumnWidget.build = function (data) {
    var element = document.createElement('div');
    element.classList.add('pygui-column');
    for (var _i = 0, _a = data.children; _i < _a.length; _i++) {
      var child = _a[_i];
      element.appendChild((0, app_1.buildWidget)(child));
    }
    return element;
  };
  ColumnWidget.update = function (element, deltaState) {};
  return ColumnWidget;
}();
exports.ColumnWidget = ColumnWidget;
},{"./app":"EVxB"}],"u1gD":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.RectangleWidget = void 0;
var app_1 = require("./app");
var RectangleWidget = /** @class */function () {
  function RectangleWidget() {}
  RectangleWidget.build = function (data) {
    var element = document.createElement('div');
    element.classList.add('pygui-rectangle');
    return element;
  };
  RectangleWidget.update = function (element, deltaState) {
    if (deltaState.fill !== undefined) {
      element.style.background = (0, app_1.fillToCss)(deltaState.fill);
    }
    if (deltaState.cornerRadius !== undefined) {
      var _a = deltaState.cornerRadius,
        topLeft = _a[0],
        topRight = _a[1],
        bottomRight = _a[2],
        bottomLeft = _a[3];
      element.style.borderRadius = "".concat(topLeft, "em ").concat(topRight, "em ").concat(bottomRight, "em ").concat(bottomLeft, "em");
    }
  };
  return RectangleWidget;
}();
exports.RectangleWidget = RectangleWidget;
},{"./app":"EVxB"}],"E2Q9":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.StackWidget = void 0;
var app_1 = require("./app");
var StackWidget = /** @class */function () {
  function StackWidget() {}
  StackWidget.build = function (data) {
    var element = document.createElement('div');
    element.classList.add('pygui-stack');
    for (var ii = 0; ii < data.children.length; ii++) {
      var childElement = (0, app_1.buildWidget)(data.children[ii]);
      childElement.style.zIndex = "".concat(ii + 1);
      element.appendChild(childElement);
    }
    return element;
  };
  StackWidget.update = function (element, deltaState) {};
  return StackWidget;
}();
exports.StackWidget = StackWidget;
},{"./app":"EVxB"}],"JoLr":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.MarginWidget = void 0;
var app_1 = require("./app");
var MarginWidget = /** @class */function () {
  function MarginWidget() {}
  MarginWidget.build = function (widget) {
    var element = document.createElement('div');
    element.appendChild((0, app_1.buildWidget)(widget.child));
    return element;
  };
  MarginWidget.update = function (element, state) {
    if (state.margin !== undefined) {
      element.style.marginLeft = "".concat(state.margin[0], "em");
      element.style.marginTop = "".concat(state.margin[1], "em");
      element.style.marginRight = "".concat(state.margin[2], "em");
      element.style.marginBottom = "".concat(state.margin[3], "em");
    }
  };
  return MarginWidget;
}();
exports.MarginWidget = MarginWidget;
},{"./app":"EVxB"}],"cKKU":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.AlignWidget = void 0;
var app_1 = require("./app");
var AlignWidget = /** @class */function () {
  function AlignWidget() {}
  AlignWidget.build = function (data) {
    var element = document.createElement('div');
    element.appendChild((0, app_1.buildWidget)(data.child));
    return element;
  };
  AlignWidget.update = function (element, state) {
    if (state.align_x !== undefined) {
      if (state.align_x === null) {
        element.style.justifyContent = 'unset';
      } else {
        element.style.justifyContent = state.align_x * 100 + '%';
      }
    }
    if (state.align_y !== undefined) {
      if (state.align_y === null) {
        element.style.alignItems = 'unset';
      } else {
        element.style.alignItems = state.align_y * 100 + '%';
      }
    }
  };
  return AlignWidget;
}();
exports.AlignWidget = AlignWidget;
},{"./app":"EVxB"}],"zONe":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ButtonWidget = void 0;
var app_1 = require("./app");
var ButtonWidget = /** @class */function () {
  function ButtonWidget() {}
  ButtonWidget.build = function (data) {
    var element = document.createElement('button');
    element.type = 'button';
    element.onclick = function () {
      (0, app_1.sendEvent)(element, 'buttonPressedEvent', {});
    };
    return element;
  };
  ButtonWidget.update = function (element, deltaState) {
    if (deltaState.text !== undefined) {
      element.textContent = deltaState.text;
    }
  };
  return ButtonWidget;
}();
exports.ButtonWidget = ButtonWidget;
},{"./app":"EVxB"}],"LKOD":[function(require,module,exports) {
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
exports.MouseEventListener = void 0;
var app_1 = require("./app");
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
var MouseEventListener = /** @class */function () {
  function MouseEventListener() {}
  MouseEventListener.build = function (data) {
    var element = document.createElement('div');
    element.appendChild((0, app_1.buildWidget)(data.child));
    return element;
  };
  MouseEventListener.update = function (element, deltaState) {
    if (deltaState.reportMouseDown) {
      element.onmousedown = function (e) {
        (0, app_1.sendEvent)(element, 'mouseDownEvent', __assign(__assign({}, eventMouseButtonToString(e)), eventMousePositionToString(e)));
      };
    } else {
      element.onmousedown = null;
    }
    if (deltaState.reportMouseUp) {
      element.onmouseup = function (e) {
        (0, app_1.sendEvent)(element, 'mouseUpEvent', __assign(__assign({}, eventMouseButtonToString(e)), eventMousePositionToString(e)));
      };
    } else {
      element.onmouseup = null;
    }
    // TODO
  };

  return MouseEventListener;
}();
exports.MouseEventListener = MouseEventListener;
},{"./app":"EVxB"}],"EVxB":[function(require,module,exports) {
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
exports.sendEvent = exports.sendJson = exports.buildWidget = exports.fillToCss = exports.colorToCss = exports.pixelsPerEm = void 0;
var text_1 = require("./text");
var row_1 = require("./row");
var column_1 = require("./column");
var rectangle_1 = require("./rectangle");
var stack_1 = require("./stack");
var margin_1 = require("./margin");
var align_1 = require("./align");
var button_1 = require("./button");
var mouse_event_listener_1 = require("./mouse_event_listener");
var initialMessages = '{initial_messages}';
var socket = null;
exports.pixelsPerEm = 16;
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
  // Invalid fill type
  throw "Invalid fill type: ".concat(fill);
}
exports.fillToCss = fillToCss;
var widgetClasses = {
  align: align_1.AlignWidget,
  button: button_1.ButtonWidget,
  column: column_1.ColumnWidget,
  margin: margin_1.MarginWidget,
  rectangle: rectangle_1.RectangleWidget,
  row: row_1.RowWidget,
  stack: stack_1.StackWidget,
  text: text_1.TextWidget,
  mouseEventListener: mouse_event_listener_1.MouseEventListener
};
function buildWidget(widget) {
  // Get the class for this widget
  var widgetClass = widgetClasses[widget.type];
  // Make sure the widget type is valid (Just helpful for debugging)
  if (!widgetClass) {
    throw "Encountered unknown widget type: ".concat(widget.type);
  }
  // Build the widget
  var result = widgetClass.build(widget);
  // Add a unique ID to the widget
  result.id = 'pygui-id-' + widget.id;
  // Store the widget's type in the element. This is used by the update
  // function to determine the correct update function to call.
  result.setAttribute('data-pygui-type', widget.type);
  // Update the widget to match its state
  widgetClass.update(result, widget);
  return result;
}
exports.buildWidget = buildWidget;
function processMessage(message) {
  if (message.type == 'replaceWidgets') {
    // Clear any previous widgets
    var body = document.getElementsByTagName('body')[0];
    body.innerHTML = '';
    // Build the HTML document
    body.appendChild(buildWidget(message.widget));
  } else {
    throw "Encountered unknown message type: ".concat(message);
  }
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
  var url = new URL('/ws', window.location.href);
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
function sendJson(message) {
  if (!socket) {
    console.log("Attempted to send message, but the websocket is not connected: ".concat(message));
    return;
  }
  socket.send(JSON.stringify(message));
}
exports.sendJson = sendJson;
function sendEvent(element, eventType, eventArgs) {
  sendJson(__assign({
    type: eventType,
    // Remove the leading `pygui-id-` from the element's ID
    widgetId: parseInt(element.id.substring(9))
  }, eventArgs));
}
exports.sendEvent = sendEvent;
main();
},{"./text":"EmPY","./row":"DCF0","./column":"FDPZ","./rectangle":"u1gD","./stack":"E2Q9","./margin":"JoLr","./align":"cKKU","./button":"zONe","./mouse_event_listener":"LKOD"}]},{},["EVxB"], null)
//# sourceMappingURL=/app.js.map