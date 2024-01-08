import { getComponentByElement } from './componentManagement';
import { updateLayout } from './layouting';
import { callRemoteMethodDiscardResponse, initWebsocket } from './rpc';

// Most of these don't have to be available in the global scope, however, since
// these are injected by Python after the build process, there have been issues
// with some build tool inlining their placeholders, which in turn lead to
// incorrect code.
//
// Assigning them to `globalThis` convinces the build tool to leave them alone.
globalThis.SESSION_TOKEN = '{session_token}';
globalThis.INITIAL_URL = '{initial_url}';
globalThis.PING_PONG_INTERVAL_SECONDS = '{ping_pong_interval}';
globalThis.RIO_DEBUG_MODE = '{debug_mode}';
globalThis.CHILD_ATTRIBUTE_NAMES = '{child_attribute_names}';

// If a debugger is present it is exposed here so the codebase can notify it as
// needed. This is an instance of `DebuggerConnectorComponent`.
globalThis.RIO_DEBUGGER = null;

function getScrollBarWidthInPixels(): number {
    let outer = document.createElement('div');
    outer.style.position = 'absolute';
    outer.style.top = '0px';
    outer.style.left = '0px';
    outer.style.visibility = 'hidden';
    outer.style.width = '200px';
    outer.style.height = '150px';
    outer.style.overflow = 'hidden';

    let inner = document.createElement('p');
    inner.style.width = '100%';
    inner.style.height = '200px';
    outer.appendChild(inner);

    document.body.appendChild(outer);
    let w1 = inner.offsetWidth;
    outer.style.overflow = 'scroll';
    let w2 = inner.offsetWidth;
    if (w1 == w2) w2 = outer.clientWidth;

    document.body.removeChild(outer);

    return w1 - w2;
}

const SCROLL_BAR_SIZE_IN_PIXELS = getScrollBarWidthInPixels();

export let pixelsPerEm = 16;
export let scrollBarSize = SCROLL_BAR_SIZE_IN_PIXELS / pixelsPerEm;

function main(): void {
    // Display a warning if running in debug mode
    if (globalThis.RIO_DEBUG_MODE) {
        console.warn(
            'Rio is running in DEBUG mode.\nDebug mode includes helpful tools for development, but is slower and disables some safety checks. Never use it in production!'
        );
    }

    // Connect to the websocket
    initWebsocket();

    // Determine the browser's font size
    var measure = document.createElement('div');
    measure.style.height = '10rem';
    document.body.appendChild(measure);
    pixelsPerEm = measure.offsetHeight / 10;
    scrollBarSize = SCROLL_BAR_SIZE_IN_PIXELS / pixelsPerEm;
    document.body.removeChild(measure);

    // Listen for URL changes, so the session can switch page
    window.addEventListener('popstate', (event) => {
        console.log(`URL changed to ${window.location.href}`);
        callRemoteMethodDiscardResponse('onUrlChange', {
            newUrl: window.location.href.toString(),
        });
    });

    // Set the initial page URL. When connecting to the server, all relevant
    // page guards execute. These may change the URL of the page, so the client
    // needs to take care to update the browser's URL to match the server's.
    window.history.replaceState(null, '', globalThis.INITIAL_URL);

    // Listen for resize events
    window.addEventListener('resize', (event) => {
        // Notify the backend
        callRemoteMethodDiscardResponse('onWindowResize', {
            newWidth: window.innerWidth / pixelsPerEm,
            newHeight: window.innerHeight / pixelsPerEm,
        });

        // Re-layout, but only if a root component already exists
        let rootElement = document.body.firstElementChild;

        if (rootElement !== null) {
            let rootInstance = getComponentByElement(
                rootElement as HTMLElement
            );
            rootInstance.makeLayoutDirty();
            updateLayout();
        }
    });
}

main();
