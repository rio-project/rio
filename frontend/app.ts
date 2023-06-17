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

const sessionToken = '{session_token}';
const initialMessages = '{initial_messages}';

let socket: WebSocket | null = null;
export var pixelsPerEm = 16;

const outerElementsToInstances = new WeakMap<HTMLElement, WidgetBase>();

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
    'Column-builtin': ColumnWidget,
    'Dropdown-builtin': DropdownWidget,
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

function updateWidgetStates(
    message: { [id: number]: WidgetState },
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
        let elementId = `reflex-id-${id}`;
        let outerElement = document.getElementById(elementId);

        // This is a reused element, nothing to do
        if (outerElement) {
            continue;
        }

        // Get the class for this widget
        const widgetClass = widgetClasses[deltaState._type_];

        // Make sure the widget type is valid (Just helpful for debugging)
        if (!widgetClass) {
            throw `Encountered unknown widget type: ${deltaState._type_}`;
        }

        // Create an instance for this widget
        let instance: WidgetBase = new widgetClass(elementId, deltaState);

        // Build the widget
        outerElement = document.createElement('div');

        let innerElement = instance.createInnerElement();
        outerElement.appendChild(innerElement);

        // Add a unique ID to the widget
        outerElement.id = elementId;

        // Add the common css class to the widget
        innerElement.classList.add('reflex-inner');
        outerElement.classList.add('reflex-outer');

        // Store the widget's class name in the element. Used for debugging.
        outerElement.setAttribute('dbg-py-class', deltaState._python_type_);

        // Set the widget's key, if it has one. Used for debugging.
        let key = deltaState['key'];
        if (key !== undefined) {
            outerElement.setAttribute('dbg-key', `${key}`);
        }

        // Create a mapping from the element to the widget instance
        outerElementsToInstances.set(outerElement, instance);

        // Keep the widget alive
        latentWidgets.appendChild(outerElement);
    }

    // Update all widgets mentioned in the message
    let widgetsNeedingGrowUpdate = new Set<WidgetBase>();

    for (let id in message) {
        let deltaState = message[id];
        let outerElement = document.getElementById('reflex-id-' + id);
        let innerElement = outerElement!.firstChild as HTMLElement;

        if (!outerElement) {
            throw `Failed to find widget with id ${id}, despite only just creating it!?`;
        }

        // Perform updates common to all widgets
        commonUpdate(outerElement, innerElement, deltaState);

        // Perform updates specific to this widget type
        let instance = outerElementsToInstances.get(
            outerElement!
        ) as WidgetBase;
        instance.updateInnerElement(innerElement, deltaState);

        // Update the widget's state
        instance.state = {
            ...instance.state,
            ...deltaState,
        };

        // Mark the widget and its children as needing a flex-grow update
        widgetsNeedingGrowUpdate.add(instance);

        for (let childElement of outerElement.childNodes) {
            let childInstance = outerElementsToInstances.get(
                childElement as any
            );

            if (childInstance !== undefined) {
                widgetsNeedingGrowUpdate.add(childInstance);
            }
        }
    }

    // Update each element's `flex-grow`. This can only be done after all
    // widgets have their correct parent set.
    widgetsNeedingGrowUpdate.forEach(updateFlexGrow);

    // Replace the root widget if requested
    if (rootWidgetId !== null) {
        let rootElement = document.getElementById(`reflex-id-${rootWidgetId}`);
        document.body.innerHTML = '';
        document.body.appendChild(rootElement!);
    }

    // Remove the latent widgets
    latentWidgets.remove();
}

function commonUpdate(
    outerElement: HTMLElement,
    innerElement: HTMLElement,
    state: WidgetState
) {
    // Margins
    if (state._margin_ !== undefined) {
        let [left, top, right, bottom] = state._margin_;

        if (left === 0) {
            innerElement.style.removeProperty('margin-left');
        } else {
            innerElement.style.marginLeft = `${left}em`;
        }

        if (top === 0) {
            innerElement.style.removeProperty('margin-top');
        } else {
            innerElement.style.marginTop = `${top}em`;
        }

        if (right === 0) {
            innerElement.style.removeProperty('margin-right');
        } else {
            innerElement.style.marginRight = `${right}em`;
        }

        if (bottom === 0) {
            innerElement.style.removeProperty('margin-bottom');
        } else {
            innerElement.style.marginBottom = `${bottom}em`;
        }
    }

    // Alignment
    if (state._align_ !== undefined) {
        let [align_x, align_y] = state._align_;

        let transform_x;
        if (align_x === null) {
            innerElement.style.removeProperty('left');
            transform_x = 0;
        } else {
            innerElement.style.left = `${align_x * 100}%`;
            transform_x = align_x * -100;
        }

        let transform_y;
        if (align_y === null) {
            innerElement.style.removeProperty('top');
            transform_y = 0;
        } else {
            innerElement.style.top = `${align_y * 100}%`;
            transform_y = align_y * -100;
        }

        if (transform_x === 0 && transform_y === 0) {
            innerElement.style.removeProperty('transform');
        } else {
            innerElement.style.transform = `translate(${transform_x}%, ${transform_y}%)`;
        }
    }

    // Width
    //
    // - If the width is set, use that
    // - Widgets with an alignment don't grow, but use their natural size
    // - Otherwise the widget's size is 100%. In this case however, margins must
    //   be taken into account, since they aren't part of the `border-box`.
    let newSize = state._size_ ? state._size_ : this.state._size_;
    let [newWidth, newHeight] = newSize;

    let newAlign = state._align_ ? state._align_ : this.state._align_;
    let [newAlignX, newAlignY] = newAlign;

    let newMargins = state._margin_ ? state._margin_ : this.state._margin_;
    let [newMarginLeft, newMarginTop, newMarginRight, newMarginBottom] =
        newMargins;
    let newMarginX = newMarginLeft + newMarginRight;
    let newMarginY = newMarginTop + newMarginBottom;

    if (newWidth !== null) {
        innerElement.style.width = `${newWidth}em`;
    } else if (newAlignX !== null) {
        innerElement.style.width = 'max-content';
    } else if (newMarginX !== 0) {
        innerElement.style.width = `calc(100% - ${newMarginX}em)`;
    } else {
        innerElement.style.removeProperty('width');
    }

    if (newHeight != null) {
        innerElement.style.height = `${newHeight}em`;
    } else if (newAlignY !== null) {
        innerElement.style.height = 'max-content';
    } else if (newMarginY !== 0) {
        innerElement.style.height = `calc(100% - ${newMarginY}em)`;
    } else {
        innerElement.style.removeProperty('height');
    }
}

function updateFlexGrow(widget: WidgetBase) {
    // Is the parent horizontally or vertically oriented?
    let outerElement = widget.outerElement;
    let parentFlexDirection = getComputedStyle(
        outerElement.parentElement!
    ).flexDirection;
    let isParentHorizontal = parentFlexDirection !== 'column';

    // Get this widget's relevant property
    let sizeIsOverridden;
    if (isParentHorizontal) {
        sizeIsOverridden = widget.state['_size_'][0] !== null;
    } else {
        sizeIsOverridden = widget.state['_size_'][1] !== null;
    }

    // If the size is overridden, don't grow
    if (sizeIsOverridden) {
        outerElement.style.flexGrow = '0';
    } else {
        outerElement.style.removeProperty('flex-grow');
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
