import { TextWidget } from './text';
import { RowWidget } from './row';
import { ColumnWidget } from './column';
import { DropdownWidget } from './dropdown';
import { RectangleWidget } from './rectangle';
import { StackWidget } from './stack';
import { Color, Fill, JsonWidget } from './models';
import { MouseEventListenerWidget } from './mouseEventListener';
import { TextInputWidget } from './textInput';
import { PlaceholderWidget } from './placeholder';
import { SwitchWidget } from './switch';

const sessionToken = '{session_token}';
const initialMessages = '{initial_messages}';

var socket: WebSocket | null = null;
export var pixelsPerEm = 16;

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

const widgetClasses = {
    column: ColumnWidget,
    rectangle: RectangleWidget,
    row: RowWidget,
    stack: StackWidget,
    text: TextWidget,
    mouseEventListener: MouseEventListenerWidget,
    textInput: TextInputWidget,
    placeholder: PlaceholderWidget,
    dropdown: DropdownWidget,
    switch: SwitchWidget,
};

function processMessage(message: any) {
    console.log('Received message: ', message);

    if (message.type == 'updateWidgetStates') {
        updateWidgetStates(message.deltaStates, message.rootWidgetId);
    } else {
        throw `Encountered unknown message type: ${message}`;
    }
}

function updateWidgetStates(
    message: { [id: number]: JsonWidget },
    rootWidgetId: number | null
) {
    // Create a HTML element to hold all latent widgets, so they aren't
    // garbage collected while updating the DOM.
    let latentWidgets = document.createElement('div');
    document.body.appendChild(latentWidgets);
    latentWidgets.id = 'reflex-latent-widgets';
    latentWidgets.style.display = 'none';

    // Make sure all widgets mentioned in the message have a corresponding HTML
    // element
    for (let id in message) {
        let deltaState = message[id];
        let element = document.getElementById('reflex-id-' + id);

        // This is a reused element, nothing to do
        if (element) {
            continue;
        }

        // Get the class for this widget
        const widgetClass = widgetClasses[deltaState._type_];

        // Make sure the widget type is valid (Just helpful for debugging)
        if (!widgetClass) {
            throw `Encountered unknown widget type: ${deltaState._type_}`;
        }

        // Build the widget
        element = widgetClass.build() as HTMLElement;

        // Add a unique ID to the widget
        element.id = 'reflex-id-' + id;

        // Add the common css class to the widget
        element.classList.add('reflex-widget');

        // Store the widget's class name in the element. Used for debugging.
        element.setAttribute('dbg-py-class', deltaState._python_type_);

        // Set the widget's key, if it has one. Used for debugging.
        let key = deltaState['key'];
        if (key !== undefined) {
            element.setAttribute('dbg-key', `${key}`);
        }

        // Keep the widget alive
        latentWidgets.appendChild(element);
    }

    // Update all widgets mentioned in the message
    for (let id in message) {
        let deltaState = message[id];
        let element = document.getElementById('reflex-id-' + id);

        if (!element) {
            throw `Failed to find widget with id ${id}, despite only just creating it!?`;
        }

        commonUpdate(element!, deltaState);

        const widgetClass = widgetClasses[deltaState._type_];
        widgetClass.update(element!, deltaState as any);
    }

    // Replace the root widget if requested
    if (rootWidgetId !== null) {
        let rootElement = document.getElementById(`reflex-id-${rootWidgetId}`);
        document.body.innerHTML = '';
        document.body.appendChild(rootElement!);
    }

    // Remove the latent widgets
    latentWidgets.remove();
}

function commonUpdate(element: HTMLElement, state: JsonWidget) {
    if (state._margin_ !== undefined) {
        element.style.marginLeft = `${state._margin_[0]}rem`;
        element.style.marginTop = `${state._margin_[1]}rem`;
        element.style.marginRight = `${state._margin_[2]}rem`;
        element.style.marginBottom = `${state._margin_[3]}rem`;
    }

    if (state._size_ !== undefined) {
        let [width, height] = state._size_;

        if (width === null) {
            element.style.removeProperty('width');
        } else {
            element.style.width = `${width}rem`;
        }

        if (height === null) {
            element.style.removeProperty('height');
        } else {
            element.style.height = `${height}rem`;
        }
    }

    if (state._align_ !== undefined) {
        let [align_x, align_y] = state._align_;

        let transform_x;
        if (align_x === null) {
            element.style.left = 'unset';
            transform_x = '0%';
        } else {
            element.style.left = `${align_x * 100}%`;
            transform_x = `${align_x * -100}%`;
        }

        let transform_y;
        if (align_y === null) {
            element.style.top = 'unset';
            transform_y = '0%';
        } else {
            element.style.top = `${align_y * 100}%`;
            transform_y = `${align_y * -100}%`;
        }

        element.style.transform = `translate(${transform_x}, ${transform_y})`;
    }
}

export function replaceOnlyChild(
    parentElement: HTMLElement,
    childId: null | undefined | number
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
    let newElement = document.getElementById('reflex-id-' + childId);

    if (!newElement) {
        throw `Failed to find replacement widget with id ${childId}`;
    }

    parentElement?.appendChild(newElement);
}

export function replaceChildren(
    parentElement: HTMLElement,
    childIds: undefined | number[]
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
                let newElement = document.getElementById('reflex-id-' + curId);
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
        if (curElement.id === 'reflex-id-' + curId) {
            curElement = curElement.nextElementSibling;
            curIdIndex++;
            continue;
        }

        // This element is not the correct element, insert the correct one
        // instead
        let newElement = document.getElementById('reflex-id-' + curId);
        parentElement.insertBefore(newElement!, curElement);
        curIdIndex++;
    }
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
    var url = new URL(`/ws?sessionToken=${sessionToken}`, window.location.href);
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

export function sendJson(message: object) {
    if (!socket) {
        console.log(
            `Attempted to send message, but the websocket is not connected: ${message}`
        );
        return;
    }

    socket.send(JSON.stringify(message));
}

export function sendEvent(
    element: HTMLElement,
    eventType: string,
    eventArgs: object
) {
    sendJson({
        type: eventType,
        // Remove the leading `reflex-id-` from the element's ID
        widgetId: parseInt(element.id.substring(10)),
        ...eventArgs,
    });
}

main();
