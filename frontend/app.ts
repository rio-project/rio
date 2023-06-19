import { TextWidget } from './text';
import { RowWidget } from './row';
import { ColumnWidget } from './column';
import { DropdownWidget } from './dropdown';
import { RectangleWidget } from './rectangle';
import { StackWidget } from './stack';
import { Color, Fill } from './models';
import { MouseEventListenerWidget } from './mouseEventListener';
import { TextInputWidget } from './textInput';
import { PlaceholderWidget } from './placeholder';
import { SwitchWidget } from './switch';
import { WidgetBase, WidgetState } from './widgetBase';
import { ProgressCircleWidget } from './progressCircle';
import { PlotWidget } from './plot';
import { AlignWidget } from './align';
import { MarginWidget } from './margin';

const sessionToken = '{session_token}';
const initialMessages = '{initial_messages}';
const CHILD_ATTRIBUTE_NAMES = {}; // {child_attribute_names};

let socket: WebSocket | null = null;
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

        return `linear-gradient(${fill.angleDegrees}deg, ${stopStrings.join(
            ', '
        )})`;
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
    let element = document.getElementById(`reflex-id-${id}`);

    if (element === null) {
        throw `Could not find widget with id ${id}`;
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
        if (curElement.id.startsWith('reflex-id-')) {
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

        if (curElement.id.match(/reflex-id-\d+$/)) {
            return curElement;
        }
    }
}

const widgetClasses = {
    'Align-builtin': AlignWidget,
    'Column-builtin': ColumnWidget,
    'Dropdown-builtin': DropdownWidget,
    'Margin-builtin': MarginWidget,
    'MouseEventListener-builtin': MouseEventListenerWidget,
    'Plot-builtin': PlotWidget,
    'ProgressCircle-builtin': ProgressCircleWidget,
    'Rectangle-builtin': RectangleWidget,
    'Row-builtin': RowWidget,
    'Stack-builtin': StackWidget,
    'Switch-builtin': SwitchWidget,
    'Text-builtin': TextWidget,
    'TextInput-builtin': TextInputWidget,
    Placeholder: PlaceholderWidget,
};

globalThis.widgetClasses = widgetClasses;

function processMessage(message: any) {
    console.log('Received message: ', message);

    if (message.type == 'updateWidgetStates') {
        updateWidgetStates(message.deltaStates, message.rootWidgetId);
    } else if (message.type == 'evaluateJavascript') {
        eval(message.javascriptSource);
    } else if (message.type == 'requestFileUpload') {
        requestFileUpload(message);
    } else {
        throw `Encountered unknown message type: ${message}`;
    }
}

function getCurrentWidgetState(
    id: number | string,
    deltaState: WidgetState
): WidgetState {
    let parentElement = document.getElementById(`reflex-id-${id}`);

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
        CHILD_ATTRIBUTE_NAMES[deltaState['_type_']!] || [];

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
        } else if (propertyValue !== null) {
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

function preprocessMessage(message: { [id: string]: WidgetState }): void {
    let originalWidgetIds = Object.keys(message);

    // Keep track of which widgets have their parents in the message
    let childIds: Set<string> = new Set();

    // Walk over all widgets in the message and inject layout widgets. The
    // message is modified in-place, so take care to have a copy of all keys
    for (let widgetId of originalWidgetIds) {
        replaceChildrenWithLayoutWidgets(message[widgetId], childIds, message);
    }

    // Find all widgets which have had a layout widget  injected, and make sure
    // their parents are updated to point to the new widget.
    for (let widgetId of originalWidgetIds) {
        // Child of another widget in the message
        if (childIds.has(widgetId)) {
            console.log(`Discarding ${widgetId} because it is a child`);
            continue;
        }

        // The parent isn't contained in the message. Find and add it.
        let childElement = document.getElementById(`reflex-id-${widgetId}`);
        if (childElement === null) {
            console.log(`Discarding ${widgetId} because it is not in the DOM`);
            continue;
        }

        let parentElement =
            getParentWidgetElementExcludingInjected(childElement);
        if (parentElement === null) {
            console.log(`Discarding ${widgetId} because it has no parent`);
            continue;
        }

        let parentInstance = elementsToInstances.get(parentElement);
        if (parentInstance === undefined) {
            throw `Parent widget with id ${parentElement} not found`;
        }

        let parentId = parentElement.id.slice('reflex-id-'.length);
        let newParentState = { ...parentInstance.state };
        replaceChildrenWithLayoutWidgets(newParentState, childIds, message);
        message[parentId] = newParentState;
        console.log(`Parent of ${widgetId} is ${parentId}`);
    }
}

function updateWidgetStates(
    message: { [id: string]: WidgetState },
    rootWidgetId: number | null
) {
    // Preprocess the message. This converts `_align_` and `_margin_` properties
    // into actual widgets, amongst other things.
    preprocessMessage(message);
    console.log(message);

    // Create a HTML element to hold all latent widgets, so they aren't
    // garbage collected while updating the DOM.
    let latentWidgets = document.createElement('div');
    document.body.appendChild(latentWidgets);
    latentWidgets.id = 'reflex-latent-widgets';
    latentWidgets.style.display = 'none';

    // Make sure all widgets mentioned in the message have a corresponding HTML
    // element
    for (let widgetId in message) {
        let deltaState = message[widgetId];
        let elementId = `reflex-id-${widgetId}`;
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
        element.classList.add('reflex-widget');

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
        document.body.innerHTML = '';
        document.body.appendChild(rootElement!);
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
        if (currentChildElement.id === `reflex-id-${childId}`) {
            return;
        }

        // Move the child element to a latent container, so it isn't garbage
        // collected
        let latentWidgets = document.getElementById('reflex-latent-widgets');
        latentWidgets?.appendChild(currentChildElement);
    }

    // Add the replacement widget
    let newElement = getElementByWidgetId(childId);
    parentElement?.appendChild(newElement);
}

export function replaceChildren(
    parentElement: HTMLElement,
    childIds: undefined | (number | string)[]
) {
    // If undefined, do nothing
    if (childIds === undefined) {
        return;
    }
    let latentWidgets = document.getElementById('reflex-latent-widgets')!;

    let curElement = parentElement.firstElementChild;
    let curIdIndex = 0;

    while (true) {
        // If there are no more children in the DOM element, add the remaining
        // children
        if (curElement === null) {
            while (curIdIndex < childIds.length) {
                let curId = childIds[curIdIndex];
                let newElement = getElementByWidgetId(curId);
                parentElement.appendChild(newElement!);
                curIdIndex++;
            }
            break;
        }

        // If there are no more children in the message, remove the remaining
        // DOM children
        if (curIdIndex >= childIds.length) {
            while (curElement !== null) {
                let nextElement = curElement.nextElementSibling;
                latentWidgets.appendChild(curElement);
                curElement = nextElement;
            }
            break;
        }

        // This element is the correct element, move on
        let curId = childIds[curIdIndex];
        if (curElement.id === `reflex-id-${curId}`) {
            curElement = curElement.nextElementSibling;
            curIdIndex++;
            continue;
        }

        // This element is not the correct element, insert the correct one
        // instead
        let newElement = getElementByWidgetId(curId);
        parentElement.insertBefore(newElement!, curElement);
        curIdIndex++;
    }
}

function requestFileUpload(message: any) {
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
    measure.style.height = '10em';
    document.body.appendChild(measure);
    pixelsPerEm = measure.offsetHeight / 10;
    document.body.removeChild(measure);

    // Process initial messages
    console.log(`Processing ${initialMessages.length} initial message(s)`);
    for (let message of initialMessages) {
        processMessage(message);
    }

    // Connect to the websocket
    var url = new URL(
        `/reflex/ws?sessionToken=${sessionToken}`,
        window.location.href
    );
    url.protocol = url.protocol.replace('http', 'ws');
    console.log(`Connecting websocket to ${url.href}`);
    socket = new WebSocket(url.href);

    socket.addEventListener('open', onOpen);
    socket.addEventListener('message', onMessage);
    socket.addEventListener('error', onError);
    socket.addEventListener('close', onClose);
}

function onOpen() {
    console.log('Connection opened');
}

function onMessage(event: any) {
    // Parse the message JSON
    let message = JSON.parse(event.data);

    // Handle it
    processMessage(message);
}

function onError(event: any) {
    console.log(`Error: ${event.message}`);
}

function onClose(event: any) {
    console.log(`Connection closed: ${event.reason}`);
}

export function sendMessageOverWebsocket(message: object) {
    if (!socket) {
        console.log(
            `Attempted to send message, but the websocket is not connected: ${message}`
        );
        return;
    }

    console.log('Sending message: ', message);

    socket.send(JSON.stringify(message));
}

main();
