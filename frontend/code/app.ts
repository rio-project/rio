import { AlignWidget } from './align';
import { ButtonWidget } from './button';
import { ClassContainerWidget } from './classContainer';
import { Color, Fill } from './models';
import { ColorPickerWidget } from './colorPicker';
import { ColumnWidget, RowWidget } from './linearContainers';
import { DropdownWidget } from './dropdown';
import { GridWidget } from './grid';
import { IconWidget } from './icon';
import { KeyEventListenerWidget } from './keyEventListener';
import { LinkWidget } from './link';
import { MarginWidget } from './margin';
import { MarkdownViewWidget } from './markdownView';
import { MediaPlayerWidget } from './mediaPlayer';
import { MouseEventListenerWidget } from './mouseEventListener';
import { PlaceholderWidget } from './placeholder';
import { PlotWidget } from './plot';
import { ProgressBarWidget } from './progressBar';
import { ProgressCircleWidget } from './progressCircle';
import { RectangleWidget } from './rectangle';
import { RevealerWidget } from './revealer';
import { ScrollContainerWidget } from './scrollContainer';
import { ScrollTargetWidget } from './scrollTarget';
import { SizeTripSwitchWidget } from './sizeTripSwitch';
import { SliderWidget } from './slider';
import { SlideshowWidget } from './slideshow';
import { StackWidget } from './stack';
import { SwitchWidget } from './switch';
import { TextInputWidget } from './textInput';
import { TextWidget } from './text';
import { WidgetBase, WidgetState } from './widgetBase';
import { DrawerWidget } from './drawer';

const sessionToken = '{session_token}';

// @ts-ignore
const pingPongIntervalSeconds: number = '{ping_pong_interval}';

// @ts-ignore
const childAttributeNames: { [id: string]: string[] } =
    '{child_attribute_names}';

globalThis.childAttributeNames = childAttributeNames;

// @ts-ignore
const INITIAL_MESSAGES: Array<object> = '{initial_messages}';

const widgetTreeRootElement = document.body.firstElementChild as HTMLElement;
const connectionLostPopup =
    widgetTreeRootElement.nextElementSibling as HTMLElement;

let websocket: WebSocket | null = null;
export var pixelsPerEm = 16;

const elementsToInstances = new WeakMap<HTMLElement, WidgetBase>();


export function colorToCss(color: Color): string {
    const [r, g, b, a] = color;
    return `rgba(${r * 255}, ${g * 255}, ${b * 255}, ${a})`;
}

export function fillToCss(fill: Fill): string {
    // Solid Color
    if (fill.type === 'solid') {
        return colorToCss(fill.color);
    }

    // Linear Gradient
    if (fill.type === 'linearGradient') {
        if (fill.stops.length == 1) {
            return colorToCss(fill.stops[0][0]);
        }

        let stopStrings: string[] = [];
        for (let i = 0; i < fill.stops.length; i++) {
            let color = fill.stops[i][0];
            let position = fill.stops[i][1];
            stopStrings.push(`${colorToCss(color)} ${position * 100}%`);
        }

        return `linear-gradient(${
            90 - fill.angleDegrees
        }deg, ${stopStrings.join(', ')})`;
    }

    // Image
    if (fill.type === 'image') {
        let cssUrl = `url('${fill.imageUrl}')`;

        if (fill.fillMode == 'fit') {
            return `${cssUrl} center/contain no-repeat`;
        } else if (fill.fillMode == 'stretch') {
            return `${cssUrl} top left / 100% 100%`;
        } else if (fill.fillMode == 'tile') {
            return `${cssUrl} left top repeat`;
        } else if (fill.fillMode == 'zoom') {
            return `${cssUrl} center/cover no-repeat`;
        } else {
            // Invalid fill mode
            // @ts-ignore
            throw `Invalid fill mode for image fill: ${fill.type}`;
        }
    }

    // Invalid fill type
    // @ts-ignore
    throw `Invalid fill type: ${fill.type}`;
}

export function getElementByWidgetId(id: number | string): HTMLElement {
    let element = document.getElementById(`rio-id-${id}`);

    if (element === null) {
        throw `Could not find html element with id ${id}`;
    }

    return element;
}

export function getInstanceByWidgetId(id: number | string): WidgetBase {
    let element = getElementByWidgetId(id);

    let instance = elementsToInstances.get(element);

    if (instance === undefined) {
        throw `Could not find widget with id ${id}`;
    }

    return instance;
}

export function getParentWidgetElementIncludingInjected(
    element: HTMLElement
): HTMLElement | null {
    let curElement = element.parentElement;

    while (curElement !== null) {
        if (curElement.id.startsWith('rio-id-')) {
            return curElement;
        }

        curElement = curElement.parentElement;
    }

    return null;
}

export function getParentWidgetElementExcludingInjected(
    element: HTMLElement
): HTMLElement | null {
    let curElement: HTMLElement | null = element;

    while (true) {
        curElement = getParentWidgetElementIncludingInjected(curElement);

        if (curElement === null) {
            return null;
        }

        if (curElement.id.match(/rio-id-\d+$/)) {
            return curElement;
        }
    }
}

const widgetClasses = {
    'Align-builtin': AlignWidget,
    'Button-builtin': ButtonWidget,
    'ClassContainer-builtin': ClassContainerWidget,
    'ColorPicker-builtin': ColorPickerWidget,
    'Column-builtin': ColumnWidget,
    'Drawer-builtin': DrawerWidget,
    'Dropdown-builtin': DropdownWidget,
    'Grid-builtin': GridWidget,
    'Icon-builtin': IconWidget,
    'KeyEventListener-builtin': KeyEventListenerWidget,
    'Link-builtin': LinkWidget,
    'Margin-builtin': MarginWidget,
    'MarkdownView-builtin': MarkdownViewWidget,
    'MediaPlayer-builtin': MediaPlayerWidget,
    'MouseEventListener-builtin': MouseEventListenerWidget,
    'Plot-builtin': PlotWidget,
    'ProgressBar-builtin': ProgressBarWidget,
    'ProgressCircle-builtin': ProgressCircleWidget,
    'Rectangle-builtin': RectangleWidget,
    'Revealer-builtin': RevealerWidget,
    'Row-builtin': RowWidget,
    'ScrollContainer-builtin': ScrollContainerWidget,
    'ScrollTarget-builtin': ScrollTargetWidget,
    'SizeTripSwitch-builtin': SizeTripSwitchWidget,
    'Slider-builtin': SliderWidget,
    'Slideshow-builtin': SlideshowWidget,
    'Stack-builtin': StackWidget,
    'Switch-builtin': SwitchWidget,
    'Text-builtin': TextWidget,
    'TextInput-builtin': TextInputWidget,
    Placeholder: PlaceholderWidget,
};

globalThis.widgetClasses = widgetClasses;

async function processMessage(message: any) {
    // If this isn't a method call, ignore it
    if (message.method === undefined) {
        return;
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
    } else if (message.method == 'registerFont') {
        await registerFont(message.params.name, message.params.urls);
        response = null;
    }

    // Invalid method
    else {
        throw `Encountered unknown RPC method: ${message.method}`;
    }

    // If this is a request, send the response
    if (message.id !== undefined) {
        let rpcResponse = {
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

        await sendMessageOverWebsocket(rpcResponse);
    }
}

async function registerFont(name: string, urls: (string | null)[]): Promise<void> {
    const VARIATIONS = [
        { weight: 'normal', style: 'normal' },
        { weight: 'bold', style: 'normal' },
        { weight: 'normal', style: 'italic' },
        { weight: 'bold', style: 'italic' },
    ];

    let promises = new Map<string, Promise<FontFace>>();

    for (let [i, url] of urls.entries()) {
        if (url === null) {
            continue;
        }

        let fontFace = new FontFace(
            name,
            `url(${url})`,
            VARIATIONS[i],
        );
        promises.set(url, fontFace.load());
    }

    let numSuccesses = 0;
    let numFailures = 0;

    for (let [url, promise] of promises.entries()) {
        let fontFace: FontFace;
        try {
            fontFace = await promise;
        } catch (error) {
            numFailures++;
            console.warn(`Failed to load font file ${url}: ${error}`);
            continue;
        }

        numSuccesses++;
        document.fonts.add(fontFace);
    }

    if (numFailures === 0) {
        console.log(`Successfully registered all ${numSuccesses} variations of font ${name}`);
    } else if (numSuccesses === 0) {
        console.warn(`Failed to register all ${numFailures} variations of font ${name}`);
    } else {
        console.warn(`Successfully registered ${numSuccesses} variations of font ${name}, but failed to register ${numFailures} variations`);
    }
}

function getCurrentWidgetState(
    id: number | string,
    deltaState: WidgetState
): WidgetState {
    let parentElement = document.getElementById(`rio-id-${id}`);

    if (parentElement === null) {
        return deltaState;
    }

    let parentInstance = elementsToInstances.get(parentElement);

    if (parentInstance === undefined) {
        return deltaState;
    }

    return {
        ...parentInstance.state,
        ...deltaState,
    };
}

function createLayoutWidgetStates(
    widgetId: number | string,
    deltaState: WidgetState,
    message: { [id: string]: WidgetState }
): number | string {
    let entireState = getCurrentWidgetState(widgetId, deltaState);
    let resultId = widgetId;

    // Margin
    let margin = entireState['_margin_']!;
    if (
        margin[0] !== 0 ||
        margin[1] !== 0 ||
        margin[2] !== 0 ||
        margin[3] !== 0
    ) {
        let marginId = `${widgetId}-margin`;
        message[marginId] = {
            _type_: 'Margin-builtin',
            _python_type_: 'Margin (injected)',
            _size_: entireState['_size_'],
            _grow_: entireState['_grow_'],
            // @ts-ignore
            child: resultId,
            margin_left: margin[0],
            margin_top: margin[1],
            margin_right: margin[2],
            margin_bottom: margin[3],
        };
        resultId = marginId;
    }

    // Align
    let align = entireState['_align_']!;
    if (align[0] !== null || align[1] !== null) {
        let alignId = `${widgetId}-align`;
        message[alignId] = {
            _type_: 'Align-builtin',
            _python_type_: 'Align (injected)',
            _size_: entireState['_size_'],
            _grow_: entireState['_grow_'],
            // @ts-ignore
            child: resultId,
            align_x: align[0],
            align_y: align[1],
        };
        resultId = alignId;
    }

    return resultId;
}

function replaceChildrenWithLayoutWidgets(
    deltaState: WidgetState,
    childIds: Set<string>,
    message: { [id: string]: WidgetState }
): void {
    let propertyNamesWithChildren =
        childAttributeNames[deltaState['_type_']!] || [];

    function cleanId(id: string): string {
        return id.split('-')[0];
    }

    for (let propertyName of propertyNamesWithChildren) {
        let propertyValue = deltaState[propertyName];

        if (Array.isArray(propertyValue)) {
            deltaState[propertyName] = propertyValue.map((childId) => {
                childId = cleanId(childId.toString());
                childIds.add(childId);
                return createLayoutWidgetStates(
                    childId,
                    message[childId] || {},
                    message
                );
            });
        } else if (propertyValue !== null && propertyValue !== undefined) {
            let childId = cleanId(propertyValue.toString());
            deltaState[propertyName] = createLayoutWidgetStates(
                childId,
                message[childId] || {},
                message
            );
            childIds.add(childId);
        }
    }
}

function preprocessDeltaStates(message: { [id: string]: WidgetState }): void {
    // Fortunately the root widget is created internally by the server, so we
    // don't need to worry about it having a margin or alignment.

    let originalWidgetIds = Object.keys(message);

    // Keep track of which widgets have their parents in the message
    let childIds: Set<string> = new Set();

    // Walk over all widgets in the message and inject layout widgets. The
    // message is modified in-place, so take care to have a copy of all keys
    for (let widgetId of originalWidgetIds) {
        replaceChildrenWithLayoutWidgets(message[widgetId], childIds, message);
    }

    // Find all widgets which have had a layout widget injected, and make sure
    // their parents are updated to point to the new widget.
    for (let widgetId of originalWidgetIds) {
        // Child of another widget in the message
        if (childIds.has(widgetId)) {
            continue;
        }

        // The parent isn't contained in the message. Find and add it.
        let childElement = document.getElementById(`rio-id-${widgetId}`);
        if (childElement === null) {
            continue;
        }

        let parentElement =
            getParentWidgetElementExcludingInjected(childElement);
        if (parentElement === null) {
            continue;
        }

        let parentInstance = elementsToInstances.get(parentElement);
        if (parentInstance === undefined) {
            throw `Parent widget with id ${parentElement} not found`;
        }

        let parentId = parentElement.id.slice('rio-id-'.length);
        let newParentState = { ...parentInstance.state };
        replaceChildrenWithLayoutWidgets(newParentState, childIds, message);
        message[parentId] = newParentState;
    }
}

function updateWidgetStates(
    message: { [id: string]: WidgetState },
    rootWidgetId: string | number | null
): void {
    // Preprocess the message. This converts `_align_` and `_margin_` properties
    // into actual widgets, amongst other things.
    preprocessDeltaStates(message);

    // Modifying the DOM makes the keyboard focus get lost. Remember which
    // element had focus, so we can restore it later.
    let focusedElement = document.activeElement;

    // Create a HTML element to hold all latent widgets, so they aren't
    // garbage collected while updating the DOM.
    let latentWidgets = document.createElement('div');
    latentWidgets.id = 'rio-latent-widgets';
    latentWidgets.style.display = 'none';
    document.body.appendChild(latentWidgets);

    // Make sure all widgets mentioned in the message have a corresponding HTML
    // element
    for (let widgetId in message) {
        let deltaState = message[widgetId];
        let elementId = `rio-id-${widgetId}`;
        let element = document.getElementById(elementId);

        // This is a reused element, no need to instantiate a new one
        if (element) {
            continue;
        }

        // Get the class for this widget
        const widgetClass = widgetClasses[deltaState._type_!];

        // Make sure the widget type is valid (Just helpful for debugging)
        if (!widgetClass) {
            throw `Encountered unknown widget type: ${deltaState._type_}`;
        }

        // Create an instance for this widget
        let instance: WidgetBase = new widgetClass(elementId, deltaState);

        // Build the widget
        element = instance.createElement();
        element.id = elementId;
        element.classList.add('rio-widget');

        // Store the widget's class name in the element. Used for debugging.
        element.setAttribute('dbg-py-class', deltaState._python_type_!);

        // Set the widget's key, if it has one. Used for debugging.
        let key = deltaState['key'];
        if (key !== undefined) {
            element.setAttribute('dbg-key', `${key}`);
        }

        // Create a mapping from the element to the widget instance
        elementsToInstances.set(element, instance);

        // Keep the widget alive
        latentWidgets.appendChild(element);
    }

    // Update all widgets mentioned in the message
    let widgetsNeedingLayoutUpdate = new Set<WidgetBase>();

    for (let id in message) {
        let deltaState = message[id];
        let element = getElementByWidgetId(id);

        // Perform updates common to all widgets
        commonUpdate(element, deltaState);

        // Perform updates specific to this widget type
        let instance = elementsToInstances.get(element!) as WidgetBase;
        instance.updateElement(element, deltaState);

        // Update the widget's state
        instance.state = {
            ...instance.state,
            ...deltaState,
        };

        // Queue the widget and its parent for a layout update
        widgetsNeedingLayoutUpdate.add(instance);

        let parentElement = getParentWidgetElementIncludingInjected(element!);
        if (parentElement) {
            let parentInstance = elementsToInstances.get(parentElement);

            if (!parentInstance) {
                throw `Failed to find parent widget for ${id}`;
            }

            widgetsNeedingLayoutUpdate.add(parentInstance);
        }
    }

    // Widgets that have changed, or had their parents changed need to have
    // their layout updated
    widgetsNeedingLayoutUpdate.forEach((widget) => {
        widget.updateChildLayouts();
    });

    // Replace the root widget if requested
    if (rootWidgetId !== null) {
        let rootElement = getElementByWidgetId(rootWidgetId);
        widgetTreeRootElement.innerHTML = '';
        widgetTreeRootElement.appendChild(rootElement);
    }

    // Restore the keyboard focus
    if (focusedElement instanceof HTMLElement) {
        focusedElement.focus();
    }

    // Remove the latent widgets
    latentWidgets.remove();
}

function commonUpdate(element: HTMLElement, state: WidgetState) {
    if (state._size_ !== undefined) {
        if (state._size_[0] === null) {
            element.style.removeProperty('min-width');
        } else {
            element.style.minWidth = `${state._size_[0]}em`;
        }

        if (state._size_[1] === null) {
            element.style.removeProperty('min-height');
        } else {
            element.style.minHeight = `${state._size_[1]}em`;
        }
    }
}

export function replaceOnlyChild(
    parentElement: HTMLElement,
    childId: null | undefined | number | string
) {
    // If undefined, do nothing
    if (childId === undefined) {
        return;
    }

    // If null, remove the child
    if (childId === null) {
        parentElement.innerHTML = '';
        return;
    }

    const currentChildElement = parentElement.firstElementChild;

    // If a child already exists, either move it to the latent container or
    // leave it alone if it's already the correct element
    if (currentChildElement !== null) {
        // Don't reparent the child if not necessary. This way things like
        // keyboard focus are preserved
        if (currentChildElement.id === `rio-id-${childId}`) {
            return;
        }

        // Move the child element to a latent container, so it isn't garbage
        // collected
        let latentWidgets = document.getElementById('rio-latent-widgets');
        latentWidgets?.appendChild(currentChildElement);
    }

    // Add the replacement widget
    let newElement = getElementByWidgetId(childId);
    parentElement?.appendChild(newElement);
}

export function replaceChildren(
    parentElement: HTMLElement,
    childIds: undefined | (number | string)[],
    wrapInDivs: boolean = false
) {
    // If undefined, do nothing
    if (childIds === undefined) {
        return;
    }
    let latentWidgets = document.getElementById('rio-latent-widgets')!;

    let curElement = parentElement.firstElementChild;
    let curIdIndex = 0;

    let wrap, unwrap;
    if (wrapInDivs) {
        wrap = (element: HTMLElement) => {
            let wrapper = document.createElement('div');
            wrapper.appendChild(element);
            return wrapper;
        };
        unwrap = (element: HTMLElement) => {
            return element.firstElementChild!;
        };
    } else {
        wrap = (element: HTMLElement) => element;
        unwrap = (element: HTMLElement) => element;
    }

    while (true) {
        // If there are no more children in the DOM element, add the remaining
        // children
        if (curElement === null) {
            while (curIdIndex < childIds.length) {
                let curId = childIds[curIdIndex];
                let newElement = getElementByWidgetId(curId);
                parentElement.appendChild(wrap(newElement!));
                curIdIndex++;
            }
            break;
        }

        // If there are no more children in the message, remove the remaining
        // DOM children
        if (curIdIndex >= childIds.length) {
            while (curElement !== null) {
                let nextElement = curElement.nextElementSibling;
                latentWidgets.appendChild(wrap(curElement));
                curElement = nextElement;
            }
            break;
        }

        // This element is the correct element, move on
        let curId = childIds[curIdIndex];
        if (unwrap(curElement).id === `rio-id-${curId}`) {
            curElement = curElement.nextElementSibling;
            curIdIndex++;
            continue;
        }

        // This element is not the correct element, insert the correct one
        // instead
        let newElement = getElementByWidgetId(curId);
        parentElement.insertBefore(wrap(newElement!), curElement);
        curIdIndex++;
    }
}

function requestFileUpload(message: any): void {
    // Create a file upload input element
    let input = document.createElement('input');
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
        const data = new FormData();

        let ii = 0;
        for (const file of input.files || []) {
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

        // Remove the input element from the DOM. Removing this too early causes
        // weird behavior in some browsers
        input.remove();
    }

    // Listen for changes to the input
    input.addEventListener('change', finish);

    // Detect if the window gains focus. This means the file upload dialog was
    // closed without selecting a file
    window.addEventListener(
        'focus',
        function () {
            // In some browsers `focus` fires before `change`. Give `change`
            // time to run first.
            this.window.setTimeout(finish, 500);
        },
        { once: true }
    );

    // Add the input element to the DOM
    document.body.appendChild(input);

    // Trigger the file upload
    input.click();
}

function main() {
    // Determine the browser's font size
    var measure = document.createElement('div');
    measure.style.height = '10rem';
    document.body.appendChild(measure);
    pixelsPerEm = measure.offsetHeight / 10;
    document.body.removeChild(measure);

    // Listen for URL changes, so the session can switch route
    window.addEventListener('popstate', (event) => {
        console.log(`URL changed to ${window.location.href}`);
        callRemoteMethodDiscardResponse('onUrlChanged', {
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

    // Connect to the websocket
    let websocket = initWebsocket();
    websocket.addEventListener('open', sendInitialMessage);

    // Process all initial messages
    for (let message of INITIAL_MESSAGES) {
        console.log('Processing initial message: ', message);
        processMessage(message);
    }
}

function initWebsocket(): WebSocket {
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

function onOpen(): void {
    console.log('Websocket connection opened');
}

function onMessage(event: any) {
    // Parse the message JSON
    let message = JSON.parse(event.data);
    console.log('Received message: ', message);

    // Handle it
    processMessage(message);
}

function onError(event: Event) {
    console.warn(`Websocket error`);
}

function onClose(event: Event) {
    console.log(`Websocket connection closed`);

    // Show the user that the connection was lost
    displayConnectionLostPopup();
    // tryReconnectWebsocket();
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
    let websocket = initWebsocket();

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

main();
