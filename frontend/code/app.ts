import { getInstanceByElement } from './componentManagement';
import { updateLayout } from './layouting';
import { callRemoteMethodDiscardResponse, initWebsocket } from './rpc';

// Most of these don't have to be available in the global scope, however, since
// these are injected by Python after the build process, there have been issues
// with some build tool inlining their placeholders, which in turn lead to
// incorrect code.
//
// Assigning them to `globalThis` convinces the build tool to leave them alone.
globalThis.SESSION_TOKEN = '{session_token}';
globalThis.PING_PONG_INTERVAL_SECONDS = '{ping_pong_interval}';
globalThis.RIO_DEBUG_MODE = '{debug_mode}';
globalThis.CHILD_ATTRIBUTE_NAMES = '{child_attribute_names}';

export let pixelsPerEm = 16;

function main() {
    // Display a warning if running in debug mode
    if (globalThis.RIO_DEBUG_MODE) {
        console.warn(
            'Rio is running in DEBUG mode.\nDebug mode includes helpful tools for development, but is slower and disables security checks. Never use it in production!'
        );
    }

    // Connect to the websocket
    initWebsocket();

    // Determine the browser's font size
    var measure = document.createElement('div');
    measure.style.height = '10rem';
    document.body.appendChild(measure);
    pixelsPerEm = measure.offsetHeight / 10;
    document.body.removeChild(measure);

    // Listen for URL changes, so the session can switch page
    window.addEventListener('popstate', (event) => {
        console.log(`URL changed to ${window.location.href}`);
        callRemoteMethodDiscardResponse('onUrlChange', {
            newUrl: window.location.href.toString(),
        });
    });

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
            let rootInstance = getInstanceByElement(rootElement as HTMLElement);
            rootInstance.makeLayoutDirty();
            updateLayout();
        }
    });
}

main();
