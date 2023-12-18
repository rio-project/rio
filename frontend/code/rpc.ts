import { visitCommaListElements } from 'typescript';
import { pixelsPerEm } from './app';
import {
    getInstanceByComponentId,
    updateComponentStates,
} from './componentManagement';
import { HtmlComponent } from './components/html';
import { initializeDebugger } from './debugger';
import {
    requestFileUpload,
    registerFont,
    closeSession,
    setTitle,
} from './rpcFunctions';
import { commitCss } from './utils';

let websocket: WebSocket | null = null;
let pingPongHandlerId: number;

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

export function setConnectionLostPopupVisible(visible: boolean): void {
    let connectionLostPopup = document.querySelector(
        '.rio-connection-lost-popup'
    ) as HTMLElement;

    if (connectionLostPopup === null) {
        return;
    }

    if (visible) {
        connectionLostPopup.style.display = 'block';
        commitCss(connectionLostPopup); // TODO: Is this actually needed here?
        connectionLostPopup.classList.add('rio-connection-lost-popup-visible');
    } else {
        connectionLostPopup.classList.remove(
            'rio-connection-lost-popup-visible'
        );
        connectionLostPopup.style.display = 'none';
    }
}

globalThis.setConnectionLostPopupVisible = setConnectionLostPopupVisible;

function createWebsocket(connectionAttempt: number = 1): WebSocket {
    let url = new URL(
        `/rio/ws?sessionToken=${globalThis.SESSION_TOKEN}`,
        window.location.href
    );
    url.protocol = url.protocol.replace('http', 'ws');
    console.log(`Connecting websocket to ${url.href}`);
    websocket = new WebSocket(url.href);

    websocket.addEventListener('open', onOpen);
    websocket.addEventListener('message', onMessage);
    websocket.addEventListener('error', onError);
    websocket.addEventListener('close', onClose.bind(null, connectionAttempt));

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
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        userSettings: userSettings,
        prefersLightTheme: !window.matchMedia('(prefers-color-scheme: dark)')
            .matches,
        windowWidth: window.innerWidth / pixelsPerEm,
        windowHeight: window.innerHeight / pixelsPerEm,
    });
}

function onOpen(): void {
    console.log('Websocket connection opened');

    setConnectionLostPopupVisible(false);

    // Some proxies kill idle websocket connections. Send pings occasionally to
    // keep the connection alive.
    pingPongHandlerId = setInterval(() => {
        sendMessageOverWebsocket({
            jsonrpc: '2.0',
            method: 'ping',
            params: ['ping'],
            id: `ping-${Date.now()}`,
        });
    }, globalThis.PING_PONG_INTERVAL_SECONDS * 1000) as any;
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

function onClose(connectionAttempt: number, event: Event) {
    // Wait a bit before trying to reconnect (again)
    if (connectionAttempt < 10) {
        let delay = 2 * connectionAttempt;

        console.log(
            `Websocket connection closed. Reconnecting in ${delay} seconds`
        );
        setTimeout(createWebsocket, delay * 1000, connectionAttempt + 1);
    } else {
        console.warn(
            `Websocket connection closed. Giving up trying to reconnect.`
        );
    }

    // Stop sending pings
    clearInterval(pingPongHandlerId);

    // Show the user that the connection was lost
    setConnectionLostPopupVisible(true);
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
    let response: JsonRpcResponse | string | null;
    let responseIsError = false;

    switch (message.method) {
        case 'updateComponentStates':
            // The component states have changed, and new components may have been
            // introduced.
            updateComponentStates(
                message.params.deltaStates,
                message.params.rootComponentId
            );

            // Notify the debugger, if any
            if (globalThis.rioDebugger !== undefined) {
                globalThis.rioDebugger.afterComponentStateChange(
                    message.params.deltaStates
                );
            }

            response = null;
            break;

        case 'evaluateJavaScript':
            // Allow the server to run JavaScript
            //
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
                console.warn(
                    `Uncaught exception in \`evaluateJavaScript\`: ${e}`
                );
            }
            break;

        case 'setKeyboardFocus':
            let instance = getInstanceByComponentId(message.params.componentId);
            // @ts-expect-error
            instance.grabKeyboardFocus();

            response = null;
            break;

        case 'setTitle':
            setTitle(message.params.title);
            response = null;
            break;

        case 'requestFileUpload':
            // Upload a file to the server
            requestFileUpload(message.params);
            response = null;
            break;

        case 'setUserSettings':
            // Persistently store user settings
            for (let key in message.params.deltaSettings) {
                localStorage.setItem(
                    `rio:userSetting:${key}`,
                    JSON.stringify(message.params.deltaSettings[key])
                );
            }
            response = null;
            break;

        case 'registerFont':
            // Load and register a new font
            await registerFont(message.params.name, message.params.urls);
            response = null;
            break;

        case 'applyTheme':
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

            // Remove the default anti-flashbang gray
            document.documentElement.style.background = '';

            response = null;
            break;

        case 'invalidSessionToken':
            // The attempt to connect to the server has failed, because the session
            // token is invalid
            console.error(
                'Reloading the page because the session token is invalid'
            );
            window.location.reload();
            response = null;
            break;

        case 'closeSession':
            closeSession();
            response = null;
            break;

        default:
            // Invalid method
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
            message: response as string,
        };
    } else {
        rpcResponse['result'] = response;
    }

    return rpcResponse;
}
