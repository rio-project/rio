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
  TextWidget.build = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-text');
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
  RowWidget.build = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-row');
    return element;
  };
  RowWidget.update = function (element, deltaState) {
    (0, app_1.replaceChildren)(element, deltaState.children);
  };
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
  ColumnWidget.build = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-column');
    return element;
  };
  ColumnWidget.update = function (element, deltaState) {
    (0, app_1.replaceChildren)(element, deltaState.children);
  };
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
  RectangleWidget.build = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-rectangle');
    return element;
  };
  RectangleWidget.update = function (element, deltaState) {
    (0, app_1.replaceOnlyChild)(element, deltaState.child);
    if (deltaState.fill !== undefined) {
      element.style.background = (0, app_1.fillToCss)(deltaState.fill);
    }
    if (deltaState.corner_radius !== undefined) {
      var _a = deltaState.corner_radius,
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
  StackWidget.build = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-stack');
    return element;
  };
  StackWidget.update = function (element, deltaState) {
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
  MarginWidget.build = function () {
    var element = document.createElement('div');
    return element;
  };
  MarginWidget.update = function (element, state) {
    (0, app_1.replaceOnlyChild)(element, state.child);
    if (state.margin_left !== undefined) {
      element.style.marginLeft = "".concat(state.margin_left, "em");
    }
    if (state.margin_top !== undefined) {
      element.style.marginTop = "".concat(state.margin_top, "em");
    }
    if (state.margin_right !== undefined) {
      element.style.marginRight = "".concat(state.margin_right, "em");
    }
    if (state.margin_bottom !== undefined) {
      element.style.marginBottom = "".concat(state.margin_bottom, "em");
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
  AlignWidget.build = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-align');
    return element;
  };
  AlignWidget.update = function (element, state) {
    (0, app_1.replaceOnlyChild)(element, state.child);
    var transform_x;
    if (state.align_x !== undefined) {
      if (state.align_x === null) {
        element.style.left = 'unset';
        transform_x = '0%';
      } else {
        element.style.left = "".concat(state.align_x * 100, "%");
        transform_x = "".concat(state.align_x * -100, "%");
      }
    }
    var transform_y;
    if (state.align_y !== undefined) {
      if (state.align_y === null) {
        element.style.top = 'unset';
        transform_y = '0%';
      } else {
        element.style.top = "".concat(state.align_y * 100, "%");
        transform_y = "".concat(state.align_y * -100, "%");
      }
    }
    element.style.transform = "translate(".concat(transform_x, ", ").concat(transform_y, ")");
  };
  return AlignWidget;
}();
exports.AlignWidget = AlignWidget;
},{"./app":"EVxB"}],"K1Om":[function(require,module,exports) {
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
  MouseEventListener.build = function () {
    var element = document.createElement('div');
    element.classList.add('reflex-mouse-event-listener');
    return element;
  };
  MouseEventListener.update = function (element, deltaState) {
    (0, app_1.replaceOnlyChild)(element, deltaState.child);
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
    if (deltaState.reportMouseMove) {
      element.onmousemove = function (e) {
        (0, app_1.sendEvent)(element, 'mouseMoveEvent', __assign({}, eventMousePositionToString(e)));
      };
    } else {
      element.onmousemove = null;
    }
    if (deltaState.reportMouseEnter) {
      element.onmouseenter = function (e) {
        (0, app_1.sendEvent)(element, 'mouseEnterEvent', __assign({}, eventMousePositionToString(e)));
      };
    } else {
      element.onmouseenter = null;
    }
    if (deltaState.reportMouseLeave) {
      element.onmouseleave = function (e) {
        (0, app_1.sendEvent)(element, 'mouseLeaveEvent', __assign({}, eventMousePositionToString(e)));
      };
    } else {
      element.onmouseleave = null;
    }
  };
  return MouseEventListener;
}();
exports.MouseEventListener = MouseEventListener;
},{"./app":"EVxB"}],"g2Fb":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.TextInputWidget = void 0;
var app_1 = require("./app");
var TextInputWidget = /** @class */function () {
  function TextInputWidget() {}
  TextInputWidget.build = function () {
    var element = document.createElement('input');
    element.classList.add('reflex-text-input');
    element.addEventListener('blur', function () {
      (0, app_1.sendEvent)(element, 'textInputBlurEvent', {
        text: element.value
      });
    });
    return element;
  };
  TextInputWidget.update = function (element, deltaState) {
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
}();
exports.TextInputWidget = TextInputWidget;
},{"./app":"EVxB"}],"X9Uo":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.OverrideWidget = void 0;
var app_1 = require("./app");
var OverrideWidget = /** @class */function () {
  function OverrideWidget() {}
  OverrideWidget.build = function () {
    var element = document.createElement('div');
    return element;
  };
  OverrideWidget.update = function (element, deltaState) {
    (0, app_1.replaceOnlyChild)(element, deltaState.child);
    if (deltaState.width !== undefined) {
      if (deltaState.width === null) {
        element.style.removeProperty('width');
      } else {
        element.style.width = "".concat(deltaState.width, "em");
      }
    }
    if (deltaState.height !== undefined) {
      if (deltaState.height === null) {
        element.style.removeProperty('height');
      } else {
        element.style.height = "".concat(deltaState.height, "em");
      }
    }
  };
  return OverrideWidget;
}();
exports.OverrideWidget = OverrideWidget;
},{"./app":"EVxB"}],"When":[function(require,module,exports) {
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.PlaceholderWidget = void 0;
var app_1 = require("./app");
var PlaceholderWidget = /** @class */function () {
  function PlaceholderWidget() {}
  PlaceholderWidget.build = function () {
    var element = document.createElement('div');
    return element;
  };
  PlaceholderWidget.update = function (element, deltaState) {
    (0, app_1.replaceOnlyChild)(element, deltaState._child_);
  };
  return PlaceholderWidget;
}();
exports.PlaceholderWidget = PlaceholderWidget;
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
exports.sendEvent = exports.sendJson = exports.replaceChildren = exports.replaceOnlyChild = exports.fillToCss = exports.colorToCss = exports.pixelsPerEm = void 0;
var text_1 = require("./text");
var row_1 = require("./row");
var column_1 = require("./column");
var rectangle_1 = require("./rectangle");
var stack_1 = require("./stack");
var margin_1 = require("./margin");
var align_1 = require("./align");
var mouseEventListener_1 = require("./mouseEventListener");
var textInput_1 = require("./textInput");
var override_1 = require("./override");
var placeholder_1 = require("./placeholder");
var sessionToken = '{session_token}';
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
  column: column_1.ColumnWidget,
  margin: margin_1.MarginWidget,
  rectangle: rectangle_1.RectangleWidget,
  row: row_1.RowWidget,
  stack: stack_1.StackWidget,
  text: text_1.TextWidget,
  mouseEventListener: mouseEventListener_1.MouseEventListener,
  textInput: textInput_1.TextInputWidget,
  override: override_1.OverrideWidget,
  placeholder: placeholder_1.PlaceholderWidget
};
function processMessage(message) {
  console.log('Received message: ', message);
  if (message.type == 'updateWidgetStates') {
    updateWidgetStates(message.deltaStates, message.rootWidgetId);
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
    var element = document.getElementById('reflex-id-' + id);
    // This is a reused element, nothing to do
    if (element) {
      continue;
    }
    // Get the class for this widget
    var widgetClass = widgetClasses[deltaState._type_];
    // Make sure the widget type is valid (Just helpful for debugging)
    if (!widgetClass) {
      throw "Encountered unknown widget type: ".concat(deltaState._type_);
    }
    // Build the widget
    element = widgetClass.build();
    // Add a unique ID to the widget
    element.id = 'reflex-id-' + id;
    // Add the common css class to the widget
    element.classList.add('reflex-widget');
    // Store the widget's class name in the element. Useful for debugging.
    element.setAttribute('data-class-name', deltaState._python_type_);
    // Keep the widget alive
    latentWidgets.appendChild(element);
  }
  // Update all widgets mentioned in the message
  for (var id in message) {
    var deltaState = message[id];
    var element = document.getElementById('reflex-id-' + id);
    if (!element) {
      throw "Failed to find widget with id ".concat(id, ", despite only just creating it!?");
    }
    var widgetClass = widgetClasses[deltaState._type_];
    widgetClass.update(element, deltaState);
  }
  // Replace the root widget if requested
  if (rootWidgetId !== null) {
    var rootElement = document.getElementById("reflex-id-".concat(rootWidgetId));
    document.body.innerHTML = '';
    document.body.appendChild(rootElement);
  }
  // Remove the latent widgets
  latentWidgets.remove();
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
  // Move the child element to a latent container, so it isn't garbage
  // collected
  if (parentElement.firstElementChild !== null) {
    var latentWidgets = document.getElementById('reflex-latent-widgets');
    latentWidgets === null || latentWidgets === void 0 ? void 0 : latentWidgets.appendChild(parentElement.firstElementChild);
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
    curElement = newElement;
    curIdIndex++;
  }
}
exports.replaceChildren = replaceChildren;
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
  var url = new URL("/ws?sessionToken=".concat(sessionToken), window.location.href);
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
    // Remove the leading `reflex-id-` from the element's ID
    widgetId: parseInt(element.id.substring(10))
  }, eventArgs));
}
exports.sendEvent = sendEvent;
main();
},{"./text":"EmPY","./row":"DCF0","./column":"FDPZ","./rectangle":"u1gD","./stack":"E2Q9","./margin":"JoLr","./align":"cKKU","./mouseEventListener":"K1Om","./textInput":"g2Fb","./override":"X9Uo","./placeholder":"When"}]},{},["EVxB"], null)
//# sourceMappingURL=/app.js.map