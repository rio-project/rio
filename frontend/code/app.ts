import {
    JsonRpcMessage,
    callRemoteMethodDiscardResponse,
    initWebsocket,
    processMessageReturnResponse,
} from './rpc';

export const sessionToken: string = '{session_token}';

// @ts-ignore
export const pingPongIntervalSeconds: number = '{ping_pong_interval}';

// @ts-ignore
export const debug_mode: boolean = '{debug_mode}';

// @ts-ignore
const childAttributeNames: { [id: string]: string[] } =
    '{child_attribute_names}';
globalThis.childAttributeNames = childAttributeNames;

export let pixelsPerEm = 16;

function main() {
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
        callRemoteMethodDiscardResponse('onWindowResize', {
            newWidth: window.innerWidth / pixelsPerEm,
            newHeight: window.innerHeight / pixelsPerEm,
        });
    });
}

main();
