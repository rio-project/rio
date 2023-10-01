import { pingPongIntervalSeconds, pixelsPerEm, sessionToken } from './app';
import { updateWidgetStates } from './widgetManagement';
import { requestFileUpload, registerFont } from './rpcFunctions';

let websocket: WebSocket | null = null;
const connectionLostPopup = document.querySelector(
    '.rio-error-popup'
) as HTMLElement;

export type JsonRpcMessage = {
    jsonrpc: '2.0';
    id?: number;
    method?: string;
    params?: any;
};

export type JsonRpcResponse = {
    jsonrpc: '2.0';
    id: number;
    result?: any;
    error?: {
        code: number;
        message: string;
    };
};

function createWebsocket(): WebSocket {
    let url = new URL(
        `/rio/ws?sessionToken=${sessionToken}`,
        window.location.href
    );
    url.protocol = url.protocol.replace('http', 'ws');
    console.log(`Connecting websocket to ${url.href}`);
    websocket = new WebSocket(url.href);

    // Some proxies kill idle websocket connections. Send pings occasionally to
    // keep the connection alive.
    //
    // Make sure to set an ID so the server replies
    let pingPongHandlerId = setInterval(() => {
        sendMessageOverWebsocket({
            jsonrpc: '2.0',
            method: 'ping',
            params: ['ping'],
            id: `ping-${Date.now()}`,
        });
    }, pingPongIntervalSeconds * 1000);

    websocket.addEventListener('open', onOpen);
    websocket.addEventListener('message', onMessage);
    websocket.addEventListener('error', onError);
    websocket.addEventListener('close', (event: CloseEvent) => {
        clearInterval(pingPongHandlerId);
        onClose(event);
    });

    return websocket;
}

export function initWebsocket(): void {
    let websocket = createWebsocket();
    websocket.addEventListener('open', sendInitialMessage);
}

function sendInitialMessage(): void {
    // Send the initial message with user information to the server
    let userSettings = {};
    for (let key in localStorage) {
        if (!key.startsWith('rio:userSetting:')) {
            continue;
        }

        try {
            userSettings[key.slice('rio:userSetting:'.length)] = JSON.parse(
                localStorage[key]
            );
        } catch (e) {
            console.warn(`Failed to parse user setting ${key}: ${e}`);
        }
    }

    sendMessageOverWebsocket({
        websiteUrl: window.location.href,
        preferredLanguages: navigator.languages,
        userSettings: userSettings,
        windowWidth: window.innerWidth / pixelsPerEm,
        windowHeight: window.innerHeight / pixelsPerEm,
    });
}

function reconnectWebsocket(attempt: number = 1): void {
    let websocket = createWebsocket();

    websocket.onerror = (event: any) => {
        // Wait a bit longer before trying again
        let delay = Math.min(1 * attempt, 15);

        console.log(`Websocket reconnect failed. Retrying in ${delay} seconds`);
        setTimeout(reconnectWebsocket, delay * 1000, attempt + 1);
    };

    websocket.onopen = () => {
        websocket.onerror = null;

        console.log('Websocket reconnect succeeded');

        connectionLostPopup.style.opacity = '0';
        connectionLostPopup.style.display = 'none';
    };
}

function onOpen(): void {
    console.log('Websocket connection opened');
}

async function onMessage(event: any) {
    // Parse the message JSON
    let message = JSON.parse(event.data);
    console.log('Received message: ', message);

    // Handle it
    let response = await processMessageReturnResponse(message);

    // If this is a request, send the response
    if (message.id !== undefined && response !== null) {
        await sendMessageOverWebsocket(response);
    }
}

function onError(event: Event) {
    console.warn(`Websocket error`);
}

function onClose(event: Event) {
    console.log(`Websocket connection closed`);

    // Show the user that the connection was lost
    displayConnectionLostPopup();
    // reconnectWebsocket();
}

export function sendMessageOverWebsocket(message: object) {
    if (!websocket) {
        console.error(
            `Attempted to send message, but the websocket is not connected: ${message}`
        );
        return;
    }

    console.log('Sending message: ', message);

    websocket.send(JSON.stringify(message));
}

export function callRemoteMethodDiscardResponse(
    method: string,
    params: object
) {
    sendMessageOverWebsocket({
        jsonrpc: '2.0',
        method: method,
        params: params,
    });
}

export async function processMessageReturnResponse(
    message: JsonRpcMessage
): Promise<JsonRpcResponse | null> {
    // If this isn't a method call, ignore it
    if (message.method === undefined) {
        return null;
    }

    // Delegate to the appropriate handler
    let response;
    let responseIsError = false;

    // New widgets received
    if (message.method == 'updateWidgetStates') {
        await updateWidgetStates(
            message.params.deltaStates,
            message.params.rootWidgetId
        );
        response = null;
    }

    // Allow the server to run JavaScript
    else if (message.method == 'evaluateJavaScript') {
        // Avoid using `eval` so that parceljs can minify the code
        try {
            const func = new Function(message.params.javaScriptSource);
            response = await func();

            if (response === undefined) {
                response = null;
            }
        } catch (e) {
            response = e.toString();
            responseIsError = true;
            console.warn(`Uncaught exception in \`evaluateJavaScript\`: ${e}`);
        }
    }

    // Upload a file to the server
    else if (message.method == 'requestFileUpload') {
        requestFileUpload(message.params);
        response = null;
    }

    // Persistently store user settings
    else if (message.method == 'setUserSettings') {
        for (let key in message.params.deltaSettings) {
            localStorage.setItem(
                `rio:userSetting:${key}`,
                JSON.stringify(message.params.deltaSettings[key])
            );
        }
        response = null;
    }

    // Load and register a new font
    else if (message.method == 'registerFont') {
        await registerFont(message.params.name, message.params.urls);
        response = null;
    }

    // Apply a theme
    else if (message.method == 'applyTheme') {
        // Set the CSS variables
        for (let key in message.params.cssVariables) {
            document.documentElement.style.setProperty(
                key,
                message.params.cssVariables[key]
            );
        }

        // Set the theme variant
        document.documentElement.setAttribute(
            'data-theme',
            message.params.themeVariant
        );

        response = null;
    }

    // Invalid method
    else {
        throw `Encountered unknown RPC method: ${message.method}`;
    }

    if (message.id === undefined) {
        return null;
    }

    let rpcResponse: JsonRpcResponse = {
        jsonrpc: '2.0',
        id: message.id,
    };

    if (responseIsError) {
        rpcResponse['error'] = {
            code: -32000,
            message: response,
        };
    } else {
        rpcResponse['result'] = response;
    }

    return rpcResponse;
}

function displayConnectionLostPopup(): void {
    connectionLostPopup.style.display = 'block';

    // The popup spawns with opacity 0. Fade it in.
    //
    // For some reason `requestAnimationFrame` doesn't work here. Use an actual
    // timeout instead.
    setTimeout(() => {
        let popupCard = connectionLostPopup.firstElementChild! as HTMLElement;

        connectionLostPopup.style.opacity = '1';
        popupCard.style.transform = 'translate(-50%, 0)';
    }, 100);
}
