// modules are defined as an array
// [ module function, map of requires ]
//
// map of requires is short require name -> numeric require
//
// anything defined in a previous bundle is accessed via the
// orig method which is the require for previous bundles

(function (modules, entry, mainEntry, parcelRequireName, globalName) {
  /* eslint-disable no-undef */
  var globalObject =
    typeof globalThis !== 'undefined'
      ? globalThis
      : typeof self !== 'undefined'
      ? self
      : typeof window !== 'undefined'
      ? window
      : typeof global !== 'undefined'
      ? global
      : {};
  /* eslint-enable no-undef */

  // Save the require from previous bundle to this closure if any
  var previousRequire =
    typeof globalObject[parcelRequireName] === 'function' &&
    globalObject[parcelRequireName];

  var cache = previousRequire.cache || {};
  // Do not use `require` to prevent Webpack from trying to bundle this call
  var nodeRequire =
    typeof module !== 'undefined' &&
    typeof module.require === 'function' &&
    module.require.bind(module);

  function newRequire(name, jumped) {
    if (!cache[name]) {
      if (!modules[name]) {
        // if we cannot find the module within our internal map or
        // cache jump to the current global require ie. the last bundle
        // that was added to the page.
        var currentRequire =
          typeof globalObject[parcelRequireName] === 'function' &&
          globalObject[parcelRequireName];
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
      var res = localRequire.resolve(x);
      return res === false ? {} : newRequire(res);
    }

    function resolve(x) {
      var id = modules[name][1][x];
      return id != null ? id : x;
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

  Object.defineProperty(newRequire, 'root', {
    get: function () {
      return globalObject[parcelRequireName];
    },
  });

  globalObject[parcelRequireName] = newRequire;

  for (var i = 0; i < entry.length; i++) {
    newRequire(entry[i]);
  }

  if (mainEntry) {
    // Expose entry point to Node, AMD or browser globals
    // Based on https://github.com/ForbesLindesay/umd/blob/master/template.js
    var mainExports = newRequire(mainEntry);

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
})({"895UQ":[function(require,module,exports) {
var global = arguments[3];
var HMR_HOST = null;
var HMR_PORT = null;
var HMR_SECURE = false;
var HMR_ENV_HASH = "d6ea1d42532a7575";
module.bundle.HMR_BUNDLE_ID = "c5675616ffa40884";
"use strict";
/* global HMR_HOST, HMR_PORT, HMR_ENV_HASH, HMR_SECURE, chrome, browser, __parcel__import__, __parcel__importScripts__, ServiceWorkerGlobalScope */ /*::
import type {
  HMRAsset,
  HMRMessage,
} from '@parcel/reporter-dev-server/src/HMRServer.js';
interface ParcelRequire {
  (string): mixed;
  cache: {|[string]: ParcelModule|};
  hotData: {|[string]: mixed|};
  Module: any;
  parent: ?ParcelRequire;
  isParcelRequire: true;
  modules: {|[string]: [Function, {|[string]: string|}]|};
  HMR_BUNDLE_ID: string;
  root: ParcelRequire;
}
interface ParcelModule {
  hot: {|
    data: mixed,
    accept(cb: (Function) => void): void,
    dispose(cb: (mixed) => void): void,
    // accept(deps: Array<string> | string, cb: (Function) => void): void,
    // decline(): void,
    _acceptCallbacks: Array<(Function) => void>,
    _disposeCallbacks: Array<(mixed) => void>,
  |};
}
interface ExtensionContext {
  runtime: {|
    reload(): void,
    getURL(url: string): string;
    getManifest(): {manifest_version: number, ...};
  |};
}
declare var module: {bundle: ParcelRequire, ...};
declare var HMR_HOST: string;
declare var HMR_PORT: string;
declare var HMR_ENV_HASH: string;
declare var HMR_SECURE: boolean;
declare var chrome: ExtensionContext;
declare var browser: ExtensionContext;
declare var __parcel__import__: (string) => Promise<void>;
declare var __parcel__importScripts__: (string) => Promise<void>;
declare var globalThis: typeof self;
declare var ServiceWorkerGlobalScope: Object;
*/ var OVERLAY_ID = "__parcel__error__overlay__";
var OldModule = module.bundle.Module;
function Module(moduleName) {
    OldModule.call(this, moduleName);
    this.hot = {
        data: module.bundle.hotData[moduleName],
        _acceptCallbacks: [],
        _disposeCallbacks: [],
        accept: function(fn) {
            this._acceptCallbacks.push(fn || function() {});
        },
        dispose: function(fn) {
            this._disposeCallbacks.push(fn);
        }
    };
    module.bundle.hotData[moduleName] = undefined;
}
module.bundle.Module = Module;
module.bundle.hotData = {};
var checkedAssets /*: {|[string]: boolean|} */ , assetsToDispose /*: Array<[ParcelRequire, string]> */ , assetsToAccept /*: Array<[ParcelRequire, string]> */ ;
function getHostname() {
    return HMR_HOST || (location.protocol.indexOf("http") === 0 ? location.hostname : "localhost");
}
function getPort() {
    return HMR_PORT || location.port;
}
// eslint-disable-next-line no-redeclare
var parent = module.bundle.parent;
if ((!parent || !parent.isParcelRequire) && typeof WebSocket !== "undefined") {
    var hostname = getHostname();
    var port = getPort();
    var protocol = HMR_SECURE || location.protocol == "https:" && !/localhost|127.0.0.1|0.0.0.0/.test(hostname) ? "wss" : "ws";
    var ws = new WebSocket(protocol + "://" + hostname + (port ? ":" + port : "") + "/");
    // Web extension context
    var extCtx = typeof chrome === "undefined" ? typeof browser === "undefined" ? null : browser : chrome;
    // Safari doesn't support sourceURL in error stacks.
    // eval may also be disabled via CSP, so do a quick check.
    var supportsSourceURL = false;
    try {
        (0, eval)('throw new Error("test"); //# sourceURL=test.js');
    } catch (err) {
        supportsSourceURL = err.stack.includes("test.js");
    }
    // $FlowFixMe
    ws.onmessage = async function(event /*: {data: string, ...} */ ) {
        checkedAssets = {} /*: {|[string]: boolean|} */ ;
        assetsToAccept = [];
        assetsToDispose = [];
        var data /*: HMRMessage */  = JSON.parse(event.data);
        if (data.type === "update") {
            // Remove error overlay if there is one
            if (typeof document !== "undefined") removeErrorOverlay();
            let assets = data.assets.filter((asset)=>asset.envHash === HMR_ENV_HASH);
            // Handle HMR Update
            let handled = assets.every((asset)=>{
                return asset.type === "css" || asset.type === "js" && hmrAcceptCheck(module.bundle.root, asset.id, asset.depsByBundle);
            });
            if (handled) {
                console.clear();
                // Dispatch custom event so other runtimes (e.g React Refresh) are aware.
                if (typeof window !== "undefined" && typeof CustomEvent !== "undefined") window.dispatchEvent(new CustomEvent("parcelhmraccept"));
                await hmrApplyUpdates(assets);
                // Dispose all old assets.
                let processedAssets = {} /*: {|[string]: boolean|} */ ;
                for(let i = 0; i < assetsToDispose.length; i++){
                    let id = assetsToDispose[i][1];
                    if (!processedAssets[id]) {
                        hmrDispose(assetsToDispose[i][0], id);
                        processedAssets[id] = true;
                    }
                }
                // Run accept callbacks. This will also re-execute other disposed assets in topological order.
                processedAssets = {};
                for(let i = 0; i < assetsToAccept.length; i++){
                    let id = assetsToAccept[i][1];
                    if (!processedAssets[id]) {
                        hmrAccept(assetsToAccept[i][0], id);
                        processedAssets[id] = true;
                    }
                }
            } else fullReload();
        }
        if (data.type === "error") {
            // Log parcel errors to console
            for (let ansiDiagnostic of data.diagnostics.ansi){
                let stack = ansiDiagnostic.codeframe ? ansiDiagnostic.codeframe : ansiDiagnostic.stack;
                console.error("\uD83D\uDEA8 [parcel]: " + ansiDiagnostic.message + "\n" + stack + "\n\n" + ansiDiagnostic.hints.join("\n"));
            }
            if (typeof document !== "undefined") {
                // Render the fancy html overlay
                removeErrorOverlay();
                var overlay = createErrorOverlay(data.diagnostics.html);
                // $FlowFixMe
                document.body.appendChild(overlay);
            }
        }
    };
    ws.onerror = function(e) {
        console.error(e.message);
    };
    ws.onclose = function() {
        console.warn("[parcel] \uD83D\uDEA8 Connection to the HMR server was lost");
    };
}
function removeErrorOverlay() {
    var overlay = document.getElementById(OVERLAY_ID);
    if (overlay) {
        overlay.remove();
        console.log("[parcel] ✨ Error resolved");
    }
}
function createErrorOverlay(diagnostics) {
    var overlay = document.createElement("div");
    overlay.id = OVERLAY_ID;
    let errorHTML = '<div style="background: black; opacity: 0.85; font-size: 16px; color: white; position: fixed; height: 100%; width: 100%; top: 0px; left: 0px; padding: 30px; font-family: Menlo, Consolas, monospace; z-index: 9999;">';
    for (let diagnostic of diagnostics){
        let stack = diagnostic.frames.length ? diagnostic.frames.reduce((p, frame)=>{
            return `${p}
<a href="/__parcel_launch_editor?file=${encodeURIComponent(frame.location)}" style="text-decoration: underline; color: #888" onclick="fetch(this.href); return false">${frame.location}</a>
${frame.code}`;
        }, "") : diagnostic.stack;
        errorHTML += `
      <div>
        <div style="font-size: 18px; font-weight: bold; margin-top: 20px;">
          🚨 ${diagnostic.message}
        </div>
        <pre>${stack}</pre>
        <div>
          ${diagnostic.hints.map((hint)=>"<div>\uD83D\uDCA1 " + hint + "</div>").join("")}
        </div>
        ${diagnostic.documentation ? `<div>📝 <a style="color: violet" href="${diagnostic.documentation}" target="_blank">Learn more</a></div>` : ""}
      </div>
    `;
    }
    errorHTML += "</div>";
    overlay.innerHTML = errorHTML;
    return overlay;
}
function fullReload() {
    if ("reload" in location) location.reload();
    else if (extCtx && extCtx.runtime && extCtx.runtime.reload) extCtx.runtime.reload();
}
function getParents(bundle, id) /*: Array<[ParcelRequire, string]> */ {
    var modules = bundle.modules;
    if (!modules) return [];
    var parents = [];
    var k, d, dep;
    for(k in modules)for(d in modules[k][1]){
        dep = modules[k][1][d];
        if (dep === id || Array.isArray(dep) && dep[dep.length - 1] === id) parents.push([
            bundle,
            k
        ]);
    }
    if (bundle.parent) parents = parents.concat(getParents(bundle.parent, id));
    return parents;
}
function updateLink(link) {
    var href = link.getAttribute("href");
    if (!href) return;
    var newLink = link.cloneNode();
    newLink.onload = function() {
        if (link.parentNode !== null) // $FlowFixMe
        link.parentNode.removeChild(link);
    };
    newLink.setAttribute("href", // $FlowFixMe
    href.split("?")[0] + "?" + Date.now());
    // $FlowFixMe
    link.parentNode.insertBefore(newLink, link.nextSibling);
}
var cssTimeout = null;
function reloadCSS() {
    if (cssTimeout) return;
    cssTimeout = setTimeout(function() {
        var links = document.querySelectorAll('link[rel="stylesheet"]');
        for(var i = 0; i < links.length; i++){
            // $FlowFixMe[incompatible-type]
            var href /*: string */  = links[i].getAttribute("href");
            var hostname = getHostname();
            var servedFromHMRServer = hostname === "localhost" ? new RegExp("^(https?:\\/\\/(0.0.0.0|127.0.0.1)|localhost):" + getPort()).test(href) : href.indexOf(hostname + ":" + getPort());
            var absolute = /^https?:\/\//i.test(href) && href.indexOf(location.origin) !== 0 && !servedFromHMRServer;
            if (!absolute) updateLink(links[i]);
        }
        cssTimeout = null;
    }, 50);
}
function hmrDownload(asset) {
    if (asset.type === "js") {
        if (typeof document !== "undefined") {
            let script = document.createElement("script");
            script.src = asset.url + "?t=" + Date.now();
            if (asset.outputFormat === "esmodule") script.type = "module";
            return new Promise((resolve, reject)=>{
                var _document$head;
                script.onload = ()=>resolve(script);
                script.onerror = reject;
                (_document$head = document.head) === null || _document$head === void 0 || _document$head.appendChild(script);
            });
        } else if (typeof importScripts === "function") {
            // Worker scripts
            if (asset.outputFormat === "esmodule") return import(asset.url + "?t=" + Date.now());
            else return new Promise((resolve, reject)=>{
                try {
                    importScripts(asset.url + "?t=" + Date.now());
                    resolve();
                } catch (err) {
                    reject(err);
                }
            });
        }
    }
}
async function hmrApplyUpdates(assets) {
    global.parcelHotUpdate = Object.create(null);
    let scriptsToRemove;
    try {
        // If sourceURL comments aren't supported in eval, we need to load
        // the update from the dev server over HTTP so that stack traces
        // are correct in errors/logs. This is much slower than eval, so
        // we only do it if needed (currently just Safari).
        // https://bugs.webkit.org/show_bug.cgi?id=137297
        // This path is also taken if a CSP disallows eval.
        if (!supportsSourceURL) {
            let promises = assets.map((asset)=>{
                var _hmrDownload;
                return (_hmrDownload = hmrDownload(asset)) === null || _hmrDownload === void 0 ? void 0 : _hmrDownload.catch((err)=>{
                    // Web extension bugfix for Chromium
                    // https://bugs.chromium.org/p/chromium/issues/detail?id=1255412#c12
                    if (extCtx && extCtx.runtime && extCtx.runtime.getManifest().manifest_version == 3) {
                        if (typeof ServiceWorkerGlobalScope != "undefined" && global instanceof ServiceWorkerGlobalScope) {
                            extCtx.runtime.reload();
                            return;
                        }
                        asset.url = extCtx.runtime.getURL("/__parcel_hmr_proxy__?url=" + encodeURIComponent(asset.url + "?t=" + Date.now()));
                        return hmrDownload(asset);
                    }
                    throw err;
                });
            });
            scriptsToRemove = await Promise.all(promises);
        }
        assets.forEach(function(asset) {
            hmrApply(module.bundle.root, asset);
        });
    } finally{
        delete global.parcelHotUpdate;
        if (scriptsToRemove) scriptsToRemove.forEach((script)=>{
            if (script) {
                var _document$head2;
                (_document$head2 = document.head) === null || _document$head2 === void 0 || _document$head2.removeChild(script);
            }
        });
    }
}
function hmrApply(bundle /*: ParcelRequire */ , asset /*:  HMRAsset */ ) {
    var modules = bundle.modules;
    if (!modules) return;
    if (asset.type === "css") reloadCSS();
    else if (asset.type === "js") {
        let deps = asset.depsByBundle[bundle.HMR_BUNDLE_ID];
        if (deps) {
            if (modules[asset.id]) {
                // Remove dependencies that are removed and will become orphaned.
                // This is necessary so that if the asset is added back again, the cache is gone, and we prevent a full page reload.
                let oldDeps = modules[asset.id][1];
                for(let dep in oldDeps)if (!deps[dep] || deps[dep] !== oldDeps[dep]) {
                    let id = oldDeps[dep];
                    let parents = getParents(module.bundle.root, id);
                    if (parents.length === 1) hmrDelete(module.bundle.root, id);
                }
            }
            if (supportsSourceURL) // Global eval. We would use `new Function` here but browser
            // support for source maps is better with eval.
            (0, eval)(asset.output);
            // $FlowFixMe
            let fn = global.parcelHotUpdate[asset.id];
            modules[asset.id] = [
                fn,
                deps
            ];
        } else if (bundle.parent) hmrApply(bundle.parent, asset);
    }
}
function hmrDelete(bundle, id) {
    let modules = bundle.modules;
    if (!modules) return;
    if (modules[id]) {
        // Collect dependencies that will become orphaned when this module is deleted.
        let deps = modules[id][1];
        let orphans = [];
        for(let dep in deps){
            let parents = getParents(module.bundle.root, deps[dep]);
            if (parents.length === 1) orphans.push(deps[dep]);
        }
        // Delete the module. This must be done before deleting dependencies in case of circular dependencies.
        delete modules[id];
        delete bundle.cache[id];
        // Now delete the orphans.
        orphans.forEach((id)=>{
            hmrDelete(module.bundle.root, id);
        });
    } else if (bundle.parent) hmrDelete(bundle.parent, id);
}
function hmrAcceptCheck(bundle /*: ParcelRequire */ , id /*: string */ , depsByBundle /*: ?{ [string]: { [string]: string } }*/ ) {
    if (hmrAcceptCheckOne(bundle, id, depsByBundle)) return true;
    // Traverse parents breadth first. All possible ancestries must accept the HMR update, or we'll reload.
    let parents = getParents(module.bundle.root, id);
    let accepted = false;
    while(parents.length > 0){
        let v = parents.shift();
        let a = hmrAcceptCheckOne(v[0], v[1], null);
        if (a) // If this parent accepts, stop traversing upward, but still consider siblings.
        accepted = true;
        else {
            // Otherwise, queue the parents in the next level upward.
            let p = getParents(module.bundle.root, v[1]);
            if (p.length === 0) {
                // If there are no parents, then we've reached an entry without accepting. Reload.
                accepted = false;
                break;
            }
            parents.push(...p);
        }
    }
    return accepted;
}
function hmrAcceptCheckOne(bundle /*: ParcelRequire */ , id /*: string */ , depsByBundle /*: ?{ [string]: { [string]: string } }*/ ) {
    var modules = bundle.modules;
    if (!modules) return;
    if (depsByBundle && !depsByBundle[bundle.HMR_BUNDLE_ID]) {
        // If we reached the root bundle without finding where the asset should go,
        // there's nothing to do. Mark as "accepted" so we don't reload the page.
        if (!bundle.parent) return true;
        return hmrAcceptCheck(bundle.parent, id, depsByBundle);
    }
    if (checkedAssets[id]) return true;
    checkedAssets[id] = true;
    var cached = bundle.cache[id];
    assetsToDispose.push([
        bundle,
        id
    ]);
    if (!cached || cached.hot && cached.hot._acceptCallbacks.length) {
        assetsToAccept.push([
            bundle,
            id
        ]);
        return true;
    }
}
function hmrDispose(bundle /*: ParcelRequire */ , id /*: string */ ) {
    var cached = bundle.cache[id];
    bundle.hotData[id] = {};
    if (cached && cached.hot) cached.hot.data = bundle.hotData[id];
    if (cached && cached.hot && cached.hot._disposeCallbacks.length) cached.hot._disposeCallbacks.forEach(function(cb) {
        cb(bundle.hotData[id]);
    });
    delete bundle.cache[id];
}
function hmrAccept(bundle /*: ParcelRequire */ , id /*: string */ ) {
    // Execute the module.
    bundle(id);
    // Run the accept callbacks in the new version of the module.
    var cached = bundle.cache[id];
    if (cached && cached.hot && cached.hot._acceptCallbacks.length) cached.hot._acceptCallbacks.forEach(function(cb) {
        var assetsToAlsoAccept = cb(function() {
            return getParents(module.bundle.root, id);
        });
        if (assetsToAlsoAccept && assetsToAccept.length) {
            assetsToAlsoAccept.forEach(function(a) {
                hmrDispose(a[0], a[1]);
            });
            // $FlowFixMe[method-unbinding]
            assetsToAccept.push.apply(assetsToAccept, assetsToAlsoAccept);
        }
    });
}

},{}],"kXQht":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "pixelsPerEm", ()=>pixelsPerEm);
parcelHelpers.export(exports, "colorToCss", ()=>colorToCss);
parcelHelpers.export(exports, "fillToCss", ()=>fillToCss);
parcelHelpers.export(exports, "getElementByWidgetId", ()=>getElementByWidgetId);
parcelHelpers.export(exports, "getInstanceByWidgetId", ()=>getInstanceByWidgetId);
parcelHelpers.export(exports, "getParentWidgetElementIncludingInjected", ()=>getParentWidgetElementIncludingInjected);
parcelHelpers.export(exports, "getParentWidgetElementExcludingInjected", ()=>getParentWidgetElementExcludingInjected);
parcelHelpers.export(exports, "replaceOnlyChild", ()=>replaceOnlyChild);
parcelHelpers.export(exports, "replaceChildren", ()=>replaceChildren);
parcelHelpers.export(exports, "sendMessageOverWebsocket", ()=>sendMessageOverWebsocket);
var _text = require("./text");
var _row = require("./row");
var _column = require("./column");
var _dropdown = require("./dropdown");
var _rectangle = require("./rectangle");
var _stack = require("./stack");
var _mouseEventListener = require("./mouseEventListener");
var _textInput = require("./textInput");
var _placeholder = require("./placeholder");
var _switch = require("./switch");
var _progressCircle = require("./progressCircle");
var _plot = require("./plot");
var _align = require("./align");
var _margin = require("./margin");
const sessionToken = "{session_token}";
const initialMessages = "{initial_messages}";
const CHILD_ATTRIBUTE_NAMES = {}; // {child_attribute_names};
let socket = null;
var pixelsPerEm = 16;
const elementsToInstances = new WeakMap();
function colorToCss(color1) {
    const [r1, g1, b1, a1] = color1;
    return `rgba(${r1 * 255}, ${g1 * 255}, ${b1 * 255}, ${a1})`;
}
function fillToCss(fill1) {
    // Solid Color
    if (fill1.type === "solid") return colorToCss(fill1.color);
    // Linear Gradient
    if (fill1.type === "linearGradient") {
        if (fill1.stops.length == 1) return colorToCss(fill1.stops[0][0]);
        let stopStrings1 = [];
        for(let i1 = 0; i1 < fill1.stops.length; i1++){
            let color1 = fill1.stops[i1][0];
            let position1 = fill1.stops[i1][1];
            stopStrings1.push(`${colorToCss(color1)} ${position1 * 100}%`);
        }
        return `linear-gradient(${fill1.angleDegrees}deg, ${stopStrings1.join(", ")})`;
    }
    // Image
    if (fill1.type === "image") {
        let cssUrl1 = `url('${fill1.imageUrl}')`;
        if (fill1.fillMode == "fit") return `${cssUrl1} center/contain no-repeat`;
        else if (fill1.fillMode == "stretch") return `${cssUrl1} top left / 100% 100%`;
        else if (fill1.fillMode == "tile") return `${cssUrl1} left top repeat`;
        else if (fill1.fillMode == "zoom") return `${cssUrl1} center/cover no-repeat`;
        else // Invalid fill mode
        // @ts-ignore
        throw `Invalid fill mode for image fill: ${fill1.type}`;
    }
    // Invalid fill type
    // @ts-ignore
    throw `Invalid fill type: ${fill1.type}`;
}
function getElementByWidgetId(id1) {
    let element1 = document.getElementById(`reflex-id-${id1}`);
    if (element1 === null) throw `Could not find widget with id ${id1}`;
    return element1;
}
function getInstanceByWidgetId(id1) {
    let element1 = getElementByWidgetId(id1);
    let instance1 = elementsToInstances.get(element1);
    if (instance1 === undefined) throw `Could not find widget with id ${id1}`;
    return instance1;
}
function getParentWidgetElementIncludingInjected(element1) {
    let curElement1 = element1.parentElement;
    while(curElement1 !== null){
        if (curElement1.id.startsWith("reflex-id-")) return curElement1;
        curElement1 = curElement1.parentElement;
    }
    return null;
}
function getParentWidgetElementExcludingInjected(element1) {
    let curElement1 = element1;
    while(true){
        curElement1 = getParentWidgetElementIncludingInjected(curElement1);
        if (curElement1 === null) return null;
        if (curElement1.id.match(/reflex-id-\d+$/)) return curElement1;
    }
}
const widgetClasses = {
    "Align-builtin": (0, _align.AlignWidget),
    "Column-builtin": (0, _column.ColumnWidget),
    "Dropdown-builtin": (0, _dropdown.DropdownWidget),
    "Margin-builtin": (0, _margin.MarginWidget),
    "MouseEventListener-builtin": (0, _mouseEventListener.MouseEventListenerWidget),
    "Plot-builtin": (0, _plot.PlotWidget),
    "ProgressCircle-builtin": (0, _progressCircle.ProgressCircleWidget),
    "Rectangle-builtin": (0, _rectangle.RectangleWidget),
    "Row-builtin": (0, _row.RowWidget),
    "Stack-builtin": (0, _stack.StackWidget),
    "Switch-builtin": (0, _switch.SwitchWidget),
    "Text-builtin": (0, _text.TextWidget),
    "TextInput-builtin": (0, _textInput.TextInputWidget),
    Placeholder: (0, _placeholder.PlaceholderWidget)
};
globalThis.widgetClasses = widgetClasses;
function processMessage(message) {
    console.log("Received message: ", message);
    if (message.type == "updateWidgetStates") updateWidgetStates(message.deltaStates, message.rootWidgetId);
    else if (message.type == "evaluateJavascript") eval(message.javascriptSource);
    else if (message.type == "requestFileUpload") requestFileUpload(message);
    else throw `Encountered unknown message type: ${message}`;
}
function getCurrentWidgetState(id1, deltaState1) {
    let parentElement1 = document.getElementById(`reflex-id-${id1}`);
    if (parentElement1 === null) return deltaState1;
    let parentInstance1 = elementsToInstances.get(parentElement1);
    if (parentInstance1 === undefined) return deltaState1;
    return {
        ...parentInstance1.state,
        ...deltaState1
    };
}
function createLayoutWidgetStates(widgetId1, deltaState1, message1) {
    let entireState1 = getCurrentWidgetState(widgetId1, deltaState1);
    let resultId1 = widgetId1;
    // Margin
    let margin1 = entireState1["_margin_"];
    if (margin1[0] !== 0 || margin1[1] !== 0 || margin1[2] !== 0 || margin1[3] !== 0) {
        let marginId1 = `${widgetId1}-margin`;
        message1[marginId1] = {
            _type_: "Margin-builtin",
            _python_type_: "Margin (injected)",
            _size_: entireState1["_size_"],
            _grow_: entireState1["_grow_"],
            // @ts-ignore
            child: resultId1,
            margin_left: margin1[0],
            margin_top: margin1[1],
            margin_right: margin1[2],
            margin_bottom: margin1[3]
        };
        resultId1 = marginId1;
    }
    // Align
    let align1 = entireState1["_align_"];
    if (align1[0] !== null || align1[1] !== null) {
        let alignId1 = `${widgetId1}-align`;
        message1[alignId1] = {
            _type_: "Align-builtin",
            _python_type_: "Align (injected)",
            _size_: entireState1["_size_"],
            _grow_: entireState1["_grow_"],
            // @ts-ignore
            child: resultId1,
            align_x: align1[0],
            align_y: align1[1]
        };
        resultId1 = alignId1;
    }
    return resultId1;
}
function replaceChildrenWithLayoutWidgets(deltaState1, childIds1, message1) {
    let propertyNamesWithChildren1 = CHILD_ATTRIBUTE_NAMES[deltaState1["_type_"]] || [];
    function cleanId1(id1) {
        return id1.split("-")[0];
    }
    for (let propertyName1 of propertyNamesWithChildren1){
        let propertyValue1 = deltaState1[propertyName1];
        if (Array.isArray(propertyValue1)) deltaState1[propertyName1] = propertyValue1.map((childId1)=>{
            childId1 = cleanId1(childId1.toString());
            childIds1.add(childId1);
            return createLayoutWidgetStates(childId1, message1[childId1] || {}, message1);
        });
        else if (propertyValue1 !== null) {
            let childId1 = cleanId1(propertyValue1.toString());
            deltaState1[propertyName1] = createLayoutWidgetStates(childId1, message1[childId1] || {}, message1);
            childIds1.add(childId1);
        }
    }
}
function preprocessMessage(message1, rootWidgetId1) {
    // Make sure the rootWidgetId is not a number, but a string. This ensures
    // that there are no false negatives when compared to an id in the message.
    if (typeof rootWidgetId1 === "number") rootWidgetId1 = rootWidgetId1.toString();
    let originalWidgetIds1 = Object.keys(message1);
    // Keep track of which widgets have their parents in the message
    let childIds1 = new Set();
    // Walk over all widgets in the message and inject layout widgets. The
    // message is modified in-place, so take care to have a copy of all keys
    for (let widgetId1 of originalWidgetIds1)replaceChildrenWithLayoutWidgets(message1[widgetId1], childIds1, message1);
    // Find all widgets which have had a layout widget injected, and make sure
    // their parents are updated to point to the new widget.
    for (let widgetId1 of originalWidgetIds1){
        // Child of another widget in the message
        if (childIds1.has(widgetId1)) {
            console.log(`Discarding ${widgetId1} because it is a child`);
            continue;
        }
        console.log([
            rootWidgetId1,
            widgetId1
        ]);
        if (widgetId1 === rootWidgetId1) {
            rootWidgetId1 = createLayoutWidgetStates(widgetId1, message1[widgetId1], message1);
            continue;
        }
        // The parent isn't contained in the message. Find and add it.
        let childElement1 = document.getElementById(`reflex-id-${widgetId1}`);
        if (childElement1 === null) {
            console.log(`Discarding ${widgetId1} because it is not in the DOM`);
            continue;
        }
        let parentElement1 = getParentWidgetElementExcludingInjected(childElement1);
        if (parentElement1 === null) {
            console.log(`Discarding ${widgetId1} because it has no parent`);
            continue;
        }
        let parentInstance1 = elementsToInstances.get(parentElement1);
        if (parentInstance1 === undefined) throw `Parent widget with id ${parentElement1} not found`;
        let parentId1 = parentElement1.id.slice(10);
        let newParentState1 = {
            ...parentInstance1.state
        };
        replaceChildrenWithLayoutWidgets(newParentState1, childIds1, message1);
        message1[parentId1] = newParentState1;
        console.log(`Parent of ${widgetId1} is ${parentId1}`);
    }
    return rootWidgetId1;
}
function updateWidgetStates(message1, rootWidgetId1) {
    // Preprocess the message. This converts `_align_` and `_margin_` properties
    // into actual widgets, amongst other things.
    rootWidgetId1 = preprocessMessage(message1, rootWidgetId1);
    console.log(message1);
    // Create a HTML element to hold all latent widgets, so they aren't
    // garbage collected while updating the DOM.
    let latentWidgets1 = document.createElement("div");
    document.body.appendChild(latentWidgets1);
    latentWidgets1.id = "reflex-latent-widgets";
    latentWidgets1.style.display = "none";
    // Make sure all widgets mentioned in the message have a corresponding HTML
    // element
    for(let widgetId1 in message1){
        let deltaState1 = message1[widgetId1];
        let elementId1 = `reflex-id-${widgetId1}`;
        let element1 = document.getElementById(elementId1);
        // This is a reused element, no need to instantiate a new one
        if (element1) continue;
        // Get the class for this widget
        const widgetClass1 = widgetClasses[deltaState1._type_];
        // Make sure the widget type is valid (Just helpful for debugging)
        if (!widgetClass1) throw `Encountered unknown widget type: ${deltaState1._type_}`;
        // Create an instance for this widget
        let instance1 = new widgetClass1(elementId1, deltaState1);
        // Build the widget
        element1 = instance1.createElement();
        element1.id = elementId1;
        element1.classList.add("reflex-widget");
        // Store the widget's class name in the element. Used for debugging.
        element1.setAttribute("dbg-py-class", deltaState1._python_type_);
        // Set the widget's key, if it has one. Used for debugging.
        let key1 = deltaState1["key"];
        if (key1 !== undefined) element1.setAttribute("dbg-key", `${key1}`);
        // Create a mapping from the element to the widget instance
        elementsToInstances.set(element1, instance1);
        // Keep the widget alive
        latentWidgets1.appendChild(element1);
    }
    // Update all widgets mentioned in the message
    let widgetsNeedingLayoutUpdate1 = new Set();
    for(let id1 in message1){
        let deltaState1 = message1[id1];
        let element1 = getElementByWidgetId(id1);
        // Perform updates common to all widgets
        commonUpdate(element1, deltaState1);
        // Perform updates specific to this widget type
        let instance1 = elementsToInstances.get(element1);
        instance1.updateElement(element1, deltaState1);
        // Update the widget's state
        instance1.state = {
            ...instance1.state,
            ...deltaState1
        };
        // Queue the widget and its parent for a layout update
        widgetsNeedingLayoutUpdate1.add(instance1);
        let parentElement1 = getParentWidgetElementIncludingInjected(element1);
        if (parentElement1) {
            let parentInstance1 = elementsToInstances.get(parentElement1);
            if (!parentInstance1) throw `Failed to find parent widget for ${id1}`;
            widgetsNeedingLayoutUpdate1.add(parentInstance1);
        }
    }
    // Widgets that have changed, or had their parents changed need to have
    // their layout updated
    widgetsNeedingLayoutUpdate1.forEach((widget1)=>{
        widget1.updateChildLayouts();
    });
    // Replace the root widget if requested
    console.log(`Root widget is ${rootWidgetId1}`);
    if (rootWidgetId1 !== null) {
        let rootElement1 = getElementByWidgetId(rootWidgetId1);
        document.body.innerHTML = "";
        document.body.appendChild(rootElement1);
    }
    // Remove the latent widgets
    latentWidgets1.remove();
}
function commonUpdate(element1, state1) {
    if (state1._size_ !== undefined) {
        if (state1._size_[0] === null) element1.style.removeProperty("min-width");
        else element1.style.minWidth = `${state1._size_[0]}em`;
        if (state1._size_[1] === null) element1.style.removeProperty("min-height");
        else element1.style.minHeight = `${state1._size_[1]}em`;
    }
}
function replaceOnlyChild(parentElement1, childId1) {
    // If undefined, do nothing
    if (childId1 === undefined) return;
    // If null, remove the child
    if (childId1 === null) {
        parentElement1.innerHTML = "";
        return;
    }
    const currentChildElement1 = parentElement1.firstElementChild;
    // If a child already exists, either move it to the latent container or
    // leave it alone if it's already the correct element
    if (currentChildElement1 !== null) {
        // Don't reparent the child if not necessary. This way things like
        // keyboard focus are preserved
        if (currentChildElement1.id === `reflex-id-${childId1}`) return;
        // Move the child element to a latent container, so it isn't garbage
        // collected
        let latentWidgets1 = document.getElementById("reflex-latent-widgets");
        latentWidgets1?.appendChild(currentChildElement1);
    }
    // Add the replacement widget
    let newElement1 = getElementByWidgetId(childId1);
    parentElement1?.appendChild(newElement1);
}
function replaceChildren(parentElement1, childIds1) {
    // If undefined, do nothing
    if (childIds1 === undefined) return;
    let latentWidgets1 = document.getElementById("reflex-latent-widgets");
    let curElement1 = parentElement1.firstElementChild;
    let curIdIndex1 = 0;
    while(true){
        // If there are no more children in the DOM element, add the remaining
        // children
        if (curElement1 === null) {
            while(curIdIndex1 < childIds1.length){
                let curId1 = childIds1[curIdIndex1];
                let newElement1 = getElementByWidgetId(curId1);
                parentElement1.appendChild(newElement1);
                curIdIndex1++;
            }
            break;
        }
        // If there are no more children in the message, remove the remaining
        // DOM children
        if (curIdIndex1 >= childIds1.length) {
            while(curElement1 !== null){
                let nextElement1 = curElement1.nextElementSibling;
                latentWidgets1.appendChild(curElement1);
                curElement1 = nextElement1;
            }
            break;
        }
        // This element is the correct element, move on
        let curId1 = childIds1[curIdIndex1];
        if (curElement1.id === `reflex-id-${curId1}`) {
            curElement1 = curElement1.nextElementSibling;
            curIdIndex1++;
            continue;
        }
        // This element is not the correct element, insert the correct one
        // instead
        let newElement1 = getElementByWidgetId(curId1);
        parentElement1.insertBefore(newElement1, curElement1);
        curIdIndex1++;
    }
}
function requestFileUpload(message1) {
    // Create a file upload input element
    let input1 = document.createElement("input");
    input1.type = "file";
    input1.multiple = message1.multiple;
    if (message1.fileExtensions !== null) input1.accept = message1.fileExtensions.join(",");
    input1.style.display = "none";
    function finish1() {
        // Don't run twice
        if (input1.parentElement === null) return;
        // Build a `FormData` object containing the files
        const data1 = new FormData();
        let ii1 = 0;
        for (const file1 of input1.files || []){
            ii1 += 1;
            data1.append("file_names", file1.name);
            data1.append("file_types", file1.type);
            data1.append("file_sizes", file1.size.toString());
            data1.append("file_streams", file1, file1.name);
        }
        // FastAPI has trouble parsing empty form data. Append a dummy value so
        // it's never empty
        data1.append("dummy", "dummy");
        // Upload the files
        fetch(message1.uploadUrl, {
            method: "PUT",
            body: data1
        });
        // Remove the input element from the DOM. Removing this too early causes
        // weird behavior in some browsers
        input1.remove();
    }
    // Listen for changes to the input
    input1.addEventListener("change", finish1);
    // Detect if the window gains focus. This means the file upload dialog was
    // closed without selecting a file
    window.addEventListener("focus", function() {
        // In some browsers `focus` fires before `change`. Give `change`
        // time to run first.
        this.window.setTimeout(finish1, 500);
    }, {
        once: true
    });
    // Add the input element to the DOM
    document.body.appendChild(input1);
    // Trigger the file upload
    input1.click();
}
function main() {
    // Determine the browser's font size
    var measure1 = document.createElement("div");
    measure1.style.height = "10em";
    document.body.appendChild(measure1);
    pixelsPerEm = measure1.offsetHeight / 10;
    document.body.removeChild(measure1);
    // Process initial messages
    console.log(`Processing ${initialMessages.length} initial message(s)`);
    for (let message1 of initialMessages)processMessage(message1);
    // Connect to the websocket
    var url1 = new URL(`/reflex/ws?sessionToken=${sessionToken}`, window.location.href);
    url1.protocol = url1.protocol.replace("http", "ws");
    console.log(`Connecting websocket to ${url1.href}`);
    socket = new WebSocket(url1.href);
    socket.addEventListener("open", onOpen);
    socket.addEventListener("message", onMessage);
    socket.addEventListener("error", onError);
    socket.addEventListener("close", onClose);
}
function onOpen() {
    console.log("Connection opened");
}
function onMessage(event1) {
    // Parse the message JSON
    let message1 = JSON.parse(event1.data);
    // Handle it
    processMessage(message1);
}
function onError(event1) {
    console.log(`Error: ${event1.message}`);
}
function onClose(event1) {
    console.log(`Connection closed: ${event1.reason}`);
}
function sendMessageOverWebsocket(message1) {
    if (!socket) {
        console.log(`Attempted to send message, but the websocket is not connected: ${message1}`);
        return;
    }
    console.log("Sending message: ", message1);
    socket.send(JSON.stringify(message1));
}
main();

},{"./text":"02xRS","./row":"51ARQ","./column":"ckPSC","./dropdown":"1XpUK","./rectangle":"gyVMW","./stack":"kV7Lm","./mouseEventListener":"l9eKP","./textInput":"cEM39","./placeholder":"4TjQP","./switch":"9Clyc","./progressCircle":"1QucM","./plot":"jvA7S","./align":"Fqlm9","./margin":"knKZS","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"02xRS":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "TextWidget", ()=>TextWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
class TextWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let containerElement = document.createElement("div");
        containerElement.classList.add("reflex-text");
        let textElement = document.createElement("div");
        containerElement.appendChild(textElement);
        return containerElement;
    }
    updateElement(containerElement, deltaState) {
        let textElement = containerElement.firstElementChild;
        if (deltaState.text !== undefined) textElement.innerText = deltaState.text;
        if (deltaState.multiline !== undefined) textElement.style.whiteSpace = deltaState.multiline ? "normal" : "nowrap";
        if (deltaState.style !== undefined) {
            const style = deltaState.style;
            textElement.style.fontFamily = style.fontName;
            textElement.style.color = (0, _app.colorToCss)(style.fontColor);
            textElement.style.fontSize = style.fontSize + "em";
            textElement.style.fontStyle = style.italic ? "italic" : "normal";
            textElement.style.fontWeight = style.fontWeight;
            textElement.style.textDecoration = style.underlined ? "underline" : "none";
            textElement.style.textTransform = style.allCaps ? "uppercase" : "none";
        }
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"aUaw8":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
/// Base class for all widgets
parcelHelpers.export(exports, "WidgetBase", ()=>WidgetBase);
var _app = require("./app");
class WidgetBase {
    constructor(elementId, state){
        this.elementId = elementId;
        this.state = state;
        this.layoutCssProperties = {};
    }
    /// Fetches the HTML element associated with this widget. This is a slow
    /// operation and should be avoided if possible.
    get element() {
        let element = document.getElementById(this.elementId);
        if (element === null) throw new Error(`Instance for element with id ${this.elementId} cannot find its element`);
        return element;
    }
    /// Update the layout relevant CSS attributes for all of the widget's
    /// children.
    updateChildLayouts() {}
    /// Used by the parent for assigning the layout relevant CSS attributes to
    /// the widget's HTML element. This function keeps track of the assigned
    /// properties, allowing it to remove properties which are no longer
    /// relevant.
    replaceLayoutCssProperties(cssProperties) {
        // Find all properties which are no longer present and remove them
        for(let key in this.layoutCssProperties)if (!(key in cssProperties)) this.element.style.removeProperty(key);
        // Set all properties which are new or changed
        for(let key in cssProperties)this.element.style.setProperty(key, cssProperties[key]);
        // Keep track of the new properties
        this.layoutCssProperties = cssProperties;
    }
    /// Send a message to the python instance corresponding to this widget. The
    /// message is an arbitrary JSON object and will be passed to the instance's
    /// `_on_message` method.
    sendMessageToBackend(message) {
        (0, _app.sendMessageOverWebsocket)({
            type: "widgetMessage",
            // Remove the leading `reflex-id-` from the element's ID
            widgetId: parseInt(this.elementId.substring(10)),
            payload: message
        });
    }
    _setStateDontNotifyBackend(deltaState) {
        // Set the state
        this.state = {
            ...this.state,
            ...deltaState
        };
        // Trigger an update
        // @ts-ignore
        this.updateElement(this.element, deltaState);
    }
    setStateAndNotifyBackend(deltaState) {
        // Set the state. This also updates the widget
        this._setStateDontNotifyBackend(deltaState);
        // Notify the backend
        (0, _app.sendMessageOverWebsocket)({
            type: "widgetStateUpdate",
            // Remove the leading `reflex-id-` from the element's ID
            widgetId: parseInt(this.elementId.substring(10)),
            deltaState: deltaState
        });
    }
}
globalThis.WidgetBase = WidgetBase;

},{"./app":"kXQht","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"jdfFI":[function(require,module,exports) {
exports.interopDefault = function(a) {
    return a && a.__esModule ? a : {
        default: a
    };
};
exports.defineInteropFlag = function(a) {
    Object.defineProperty(a, "__esModule", {
        value: true
    });
};
exports.exportAll = function(source, dest) {
    Object.keys(source).forEach(function(key) {
        if (key === "default" || key === "__esModule" || dest.hasOwnProperty(key)) return;
        Object.defineProperty(dest, key, {
            enumerable: true,
            get: function() {
                return source[key];
            }
        });
    });
    return dest;
};
exports.export = function(dest, destName, get) {
    Object.defineProperty(dest, destName, {
        enumerable: true,
        get: get
    });
};

},{}],"51ARQ":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "RowWidget", ()=>RowWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
class RowWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.classList.add("reflex-row");
        return element;
    }
    updateElement(element, deltaState) {
        (0, _app.replaceChildren)(element, deltaState.children);
        if (deltaState.spacing !== undefined) element.style.gap = `${deltaState.spacing}em`;
    }
    updateChildLayouts() {
        let children = [];
        let anyGrowers = false;
        for (let childId of this.state["children"]){
            let child = (0, _app.getInstanceByWidgetId)(childId);
            children.push(child);
            anyGrowers = anyGrowers || child.state["_grow_"][0];
        }
        for (let child of children)child.replaceLayoutCssProperties({
            "flex-grow": !anyGrowers || child.state["_grow_"][0] ? "1" : "0"
        });
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"ckPSC":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ColumnWidget", ()=>ColumnWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
class ColumnWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.classList.add("reflex-column");
        return element;
    }
    updateElement(element, deltaState) {
        (0, _app.replaceChildren)(element, deltaState.children);
        if (deltaState.spacing !== undefined) element.style.gap = `${deltaState.spacing}em`;
    }
    updateChildLayouts() {
        let children = [];
        let anyGrowers = false;
        for (let childId of this.state["children"]){
            let child = (0, _app.getInstanceByWidgetId)(childId);
            children.push(child);
            anyGrowers = anyGrowers || child.state["_grow_"][1];
        }
        for (let child of children)child.replaceLayoutCssProperties({
            "flex-grow": !anyGrowers || child.state["_grow_"][1] ? "1" : "0"
        });
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"1XpUK":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "DropdownWidget", ()=>DropdownWidget);
var _widgetBase = require("./widgetBase");
class DropdownWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("select");
        element.classList.add("reflex-dropdown");
        element.addEventListener("input", ()=>{
            this.sendMessageToBackend({
                name: element.value
            });
        });
        return element;
    }
    updateElement(element, deltaState) {
        if (deltaState.optionNames !== undefined) {
            element.innerHTML = "";
            for (let optionName of deltaState.optionNames){
                let option = document.createElement("option");
                option.value = optionName;
                option.text = optionName;
                element.appendChild(option);
            }
        }
        if (deltaState.selectedName !== undefined) {
            if (deltaState.selectedName === null) element.selectedIndex = -1;
            else element.value = deltaState.selectedName;
        }
    }
}

},{"./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"gyVMW":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "RectangleWidget", ()=>RectangleWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
function setBoxStyleVariables(element, style, prefix, suffix) {
    // Do nothing if no style was passed
    if (style === undefined) return;
    // Define a set of CSS variables which should be set. For now without the
    // prefix
    let variables = {};
    if (style === null) variables = {
        background: "transparent",
        "stroke-color": "transparent",
        "stroke-width": "0em",
        "corner-radius-top-left": "0em",
        "corner-radius-top-right": "0em",
        "corner-radius-bottom-right": "0em",
        "corner-radius-bottom-left": "0em",
        "shadow-color": "transparent",
        "shadow-radius": "0em",
        "shadow-offset-x": "0em",
        "shadow-offset-y": "0em"
    };
    else {
        variables["background"] = (0, _app.fillToCss)(style.fill);
        variables["stroke-color"] = (0, _app.colorToCss)(style.strokeColor);
        variables["stroke-width"] = `${style.strokeWidth}em`;
        variables["corner-radius-top-left"] = `${style.cornerRadius[0]}em`;
        variables["corner-radius-top-right"] = `${style.cornerRadius[1]}em`;
        variables["corner-radius-bottom-right"] = `${style.cornerRadius[2]}em`;
        variables["corner-radius-bottom-left"] = `${style.cornerRadius[3]}em`;
        variables["shadow-color"] = (0, _app.colorToCss)(style.shadowColor);
        variables["shadow-radius"] = `${style.shadowRadius}em`;
        variables["shadow-offset-x"] = `${style.shadowOffset[0]}em`;
        variables["shadow-offset-y"] = `${style.shadowOffset[1]}em`;
    }
    // Set the variables and add the prefix
    for (const [key, value] of Object.entries(variables))element.style.setProperty(`--${prefix}${key}${suffix}`, value);
}
class RectangleWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.classList.add("reflex-rectangle");
        element.classList.add("reflex-single-container");
        return element;
    }
    updateElement(element, deltaState) {
        (0, _app.replaceOnlyChild)(element, deltaState.child);
        setBoxStyleVariables(element, deltaState.style, "rectangle-", "");
        if (deltaState.transition_time !== undefined) element.style.transitionDuration = `${deltaState.transition_time}s`;
        if (deltaState.hover_style === null) element.classList.remove("reflex-rectangle-hover");
        else if (deltaState.hover_style !== undefined) {
            element.classList.add("reflex-rectangle-hover");
            setBoxStyleVariables(element, deltaState.hover_style, "rectangle-", "-hover");
        }
        if (deltaState.cursor !== undefined) {
            if (deltaState.cursor === "default") element.style.removeProperty("cursor");
            else element.style.cursor = deltaState.cursor;
        }
    }
    updateChildLayouts() {
        let child = this.state["child"];
        if (child !== undefined && child !== null) (0, _app.getInstanceByWidgetId)(child).replaceLayoutCssProperties({});
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"kV7Lm":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "StackWidget", ()=>StackWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
class StackWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.classList.add("reflex-stack");
        return element;
    }
    updateElement(element, deltaState) {
        if (deltaState.children !== undefined) {
            (0, _app.replaceChildren)(element, deltaState.children);
            let zIndex = 0;
            for (let child of element.children){
                child.style.zIndex = `${zIndex}`;
                zIndex += 1;
            }
        }
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"l9eKP":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "MouseEventListenerWidget", ()=>MouseEventListenerWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
function eventMouseButtonToString(event) {
    return {
        button: [
            "left",
            "middle",
            "right"
        ][event.button]
    };
}
function eventMousePositionToString(event) {
    return {
        x: event.clientX / (0, _app.pixelsPerEm),
        y: event.clientY / (0, _app.pixelsPerEm)
    };
}
class MouseEventListenerWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.classList.add("reflex-single-container");
        return element;
    }
    updateElement(element, deltaState) {
        (0, _app.replaceOnlyChild)(element, deltaState.child);
        if (deltaState.reportMouseDown) element.onmousedown = (e)=>{
            this.sendMessageToBackend({
                type: "mouseDown",
                ...eventMouseButtonToString(e),
                ...eventMousePositionToString(e)
            });
        };
        else element.onmousedown = null;
        if (deltaState.reportMouseUp) element.onmouseup = (e)=>{
            this.sendMessageToBackend({
                type: "mouseUp",
                ...eventMouseButtonToString(e),
                ...eventMousePositionToString(e)
            });
        };
        else element.onmouseup = null;
        if (deltaState.reportMouseMove) element.onmousemove = (e)=>{
            this.sendMessageToBackend({
                type: "mouseMove",
                ...eventMousePositionToString(e)
            });
        };
        else element.onmousemove = null;
        if (deltaState.reportMouseEnter) element.onmouseenter = (e)=>{
            this.sendMessageToBackend({
                type: "mouseEnter",
                ...eventMousePositionToString(e)
            });
        };
        else element.onmouseenter = null;
        if (deltaState.reportMouseLeave) element.onmouseleave = (e)=>{
            this.sendMessageToBackend({
                type: "mouseLeave",
                ...eventMousePositionToString(e)
            });
        };
        else element.onmouseleave = null;
    }
    updateChildLayouts() {
        (0, _app.getInstanceByWidgetId)(this.state["child"]).replaceLayoutCssProperties({});
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"cEM39":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "TextInputWidget", ()=>TextInputWidget);
var _widgetBase = require("./widgetBase");
class TextInputWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("input");
        element.classList.add("reflex-text-input");
        // Detect value changes and send them to the backend
        element.addEventListener("blur", ()=>{
            this.setStateAndNotifyBackend({
                text: element.value
            });
        });
        // Detect the enter key and send it to the backend
        //
        // In addition to notifying the backend, also include the input's
        // current value. This ensures any event handlers actually use the up-to
        // date value.
        element.addEventListener("keydown", (event)=>{
            if (event.key === "Enter") this.sendMessageToBackend({
                text: element.value
            });
        });
        return element;
    }
    updateElement(element, deltaState) {
        let cast_element = element;
        if (deltaState.secret !== undefined) cast_element.type = deltaState.secret ? "password" : "text";
        if (deltaState.text !== undefined) cast_element.value = deltaState.text;
        if (deltaState.placeholder !== undefined) cast_element.placeholder = deltaState.placeholder;
    }
}

},{"./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"4TjQP":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "PlaceholderWidget", ()=>PlaceholderWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
class PlaceholderWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.classList.add("reflex-single-container");
        return element;
    }
    updateElement(element, deltaState) {
        (0, _app.replaceOnlyChild)(element, deltaState._child_);
    }
    updateChildLayouts() {
        (0, _app.getInstanceByWidgetId)(this.state["_child_"]).replaceLayoutCssProperties({});
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"9Clyc":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "SwitchWidget", ()=>SwitchWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
class SwitchWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.classList.add("reflex-switch");
        let containerElement = document.createElement("div");
        containerElement.classList.add("container");
        element.appendChild(containerElement);
        let checkboxElement = document.createElement("input");
        checkboxElement.type = "checkbox";
        containerElement.appendChild(checkboxElement);
        let knobElement = document.createElement("div");
        knobElement.classList.add("knob");
        containerElement.appendChild(knobElement);
        checkboxElement.addEventListener("change", ()=>{
            this.setStateAndNotifyBackend({
                is_on: checkboxElement.checked
            });
        });
        return element;
    }
    updateElement(element, deltaState) {
        if (deltaState.is_on !== undefined) {
            if (deltaState.is_on) element.classList.add("is-on");
            else element.classList.remove("is-on");
            // Assign the new value to the checkbox element, but only if it
            // differs from the current value, to avoid immediately triggering
            // the event again.
            let checkboxElement = element.querySelector("input");
            if (checkboxElement?.checked !== deltaState.is_on) checkboxElement.checked = deltaState.is_on;
        }
        if (deltaState.knobColorOff !== undefined) element.style.setProperty("--switch-knob-color-off", (0, _app.colorToCss)(deltaState.knobColorOff));
        if (deltaState.knobColorOn !== undefined) element.style.setProperty("--switch-knob-color-on", (0, _app.colorToCss)(deltaState.knobColorOn));
        if (deltaState.backgroundColorOff !== undefined) element.style.setProperty("--switch-background-color-off", (0, _app.colorToCss)(deltaState.backgroundColorOff));
        if (deltaState.backgroundColorOn !== undefined) element.style.setProperty("--switch-background-color-on", (0, _app.colorToCss)(deltaState.backgroundColorOn));
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"1QucM":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "ProgressCircleWidget", ()=>ProgressCircleWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
class ProgressCircleWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.innerHTML = `
            <svg viewBox="25 25 50 50">
                <circle class="background" cx="50" cy="50" r="20"></circle>
                <circle class="progress" cx="50" cy="50" r="20"></circle>
            </svg>
        `;
        element.classList.add("reflex-progress-circle");
        return element;
    }
    updateElement(element, deltaState) {
        if (deltaState.color !== undefined) element.style.stroke = (0, _app.colorToCss)(deltaState.color);
        if (deltaState.background_color !== undefined) element.style.setProperty("--background-color", (0, _app.colorToCss)(deltaState.background_color));
        if (deltaState.progress !== undefined) {
            if (deltaState.progress === null) element.classList.add("spinning");
            else {
                element.classList.remove("spinning");
                let fullCircle = 40 * Math.PI;
                element.style.setProperty("--dasharray", `${deltaState.progress * fullCircle}, ${(1 - deltaState.progress) * fullCircle}`);
            }
        }
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"jvA7S":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "PlotWidget", ()=>PlotWidget);
var _widgetBase = require("./widgetBase");
function loadPlotly(callback) {
    if (typeof Plotly === "undefined") {
        console.log("Fetching plotly.js");
        let script = document.createElement("script");
        script.src = "/reflex/asset/plotly.min.js";
        script.onload = callback;
        document.head.appendChild(script);
    } else callback();
}
class PlotWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.style.display = "inline-block";
        return element;
    }
    updateElement(element, deltaState) {
        if (deltaState.plotJson !== undefined) {
            element.innerHTML = "";
            loadPlotly(()=>{
                let plotJson = JSON.parse(deltaState.plotJson);
                Plotly.newPlot(element, plotJson.data, plotJson.layout, {
                    responsive: true
                });
            });
        }
    }
}

},{"./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"Fqlm9":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "AlignWidget", ()=>AlignWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
class AlignWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.classList.add("reflex-align");
        return element;
    }
    updateElement(element, deltaState) {
        (0, _app.replaceOnlyChild)(element, deltaState.child);
    }
    updateChildLayouts() {
        // Prepare the list of CSS properties to apply to the child
        let align_x = this.state["align_x"];
        let align_y = this.state["align_y"];
        let cssProperties = {};
        let transform_x;
        if (align_x === null) {
            cssProperties["width"] = "100%";
            transform_x = 0;
        } else {
            cssProperties["width"] = "max-content";
            cssProperties["left"] = `${align_x * 100}%`;
            transform_x = align_x * -100;
        }
        let transform_y;
        if (align_y === null) {
            cssProperties["height"] = "100%";
            transform_y = 0;
        } else {
            cssProperties["height"] = "max-content";
            cssProperties["top"] = `${align_y * 100}%`;
            transform_y = align_y * -100;
        }
        if (transform_x !== 0 || transform_y !== 0) cssProperties["transform"] = `translate(${transform_x}%, ${transform_y}%)`;
        // Apply the CSS properties to the child
        (0, _app.getInstanceByWidgetId)(this.state["child"]).replaceLayoutCssProperties(cssProperties);
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}],"knKZS":[function(require,module,exports) {
var parcelHelpers = require("@parcel/transformer-js/src/esmodule-helpers.js");
parcelHelpers.defineInteropFlag(exports);
parcelHelpers.export(exports, "MarginWidget", ()=>MarginWidget);
var _app = require("./app");
var _widgetBase = require("./widgetBase");
class MarginWidget extends (0, _widgetBase.WidgetBase) {
    createElement() {
        let element = document.createElement("div");
        element.classList.add("reflex-margin");
        element.classList.add("reflex-single-container");
        return element;
    }
    updateElement(element, deltaState) {
        (0, _app.replaceOnlyChild)(element, deltaState.child);
        if (deltaState.margin_left !== undefined) element.style.paddingLeft = `${deltaState.margin_left}em`;
        if (deltaState.margin_top !== undefined) element.style.paddingTop = `${deltaState.margin_top}em`;
        if (deltaState.margin_right !== undefined) element.style.paddingRight = `${deltaState.margin_right}em`;
        if (deltaState.margin_bottom !== undefined) element.style.paddingBottom = `${deltaState.margin_bottom}em`;
    }
    updateChildLayouts() {
        // let marginX = this.state['margin_left']! + this.state['margin_right']!;
        // let marginY = this.state['margin_top']! + this.state['margin_bottom']!;
        // getInstanceByWidgetId(this.state['child']).replaceLayoutCssProperties({
        //     'margin-left': `${this.state['margin_left']}em`,
        //     'margin-top': `${this.state['margin_top']}em`,
        //     'margin-right': `${this.state['margin_right']}em`,
        //     'margin-bottom': `${this.state['margin_bottom']}em`,
        //     width: `calc(100% - ${marginX}em)`,
        //     height: `calc(100% - ${marginY}em)`,
        // });
        (0, _app.getInstanceByWidgetId)(this.state["child"]).replaceLayoutCssProperties({});
    }
}

},{"./app":"kXQht","./widgetBase":"aUaw8","@parcel/transformer-js/src/esmodule-helpers.js":"jdfFI"}]},["895UQ","kXQht"], "kXQht", "parcelRequire94c2")

//# sourceMappingURL=app.js.map
