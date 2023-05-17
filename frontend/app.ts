import { TextWidget } from './text';
import { RowWidget } from './row';
import { ColumnWidget } from './column';
import { RectangleWidget } from './rectangle';
import { StackWidget } from './stack';
import { MarginWidget } from './margin';
import { AlignWidget } from './align';
import { Color, Fill, JsonWidget } from './models';
import { MouseEventListener } from './mouseEventListener';
import { TextInputWidget } from './textInput';
import { OverrideWidget } from './override';

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

    // Invalid fill type
    throw `Invalid fill type: ${fill}`;
}

const widgetClasses = {
    align: AlignWidget,
    column: ColumnWidget,
    margin: MarginWidget,
    rectangle: RectangleWidget,
    row: RowWidget,
    stack: StackWidget,
    text: TextWidget,
    mouseEventListener: MouseEventListener,
    textInput: TextInputWidget,
    override: OverrideWidget,
};

export function buildWidget(widget: JsonWidget): HTMLElement {
    // Get the class for this widget
    const widgetClass = widgetClasses[widget.type];

    // Make sure the widget type is valid (Just helpful for debugging)
    if (!widgetClass) {
        throw `Encountered unknown widget type: ${widget.type}`;
    }

    // Build the widget
    const result = widgetClass.build(widget as any);

    // Add a unique ID to the widget
    result.id = 'reflex-id-' + widget.id;

    // Add the common css class to the widget
    result.classList.add('reflex-widget');

    // Store the widget's type in the element. This is used by the update
    // function to determine the correct update function to call.
    result.setAttribute('data-reflex-type', widget.type);

    // Update the widget to match its state
    widgetClass.update(result, widget as any);

    return result;
}

function processMessage(message: any) {
    if (message.type == 'replaceWidgets') {
        // Clear any previous widgets
        let body = document.getElementsByTagName('body')[0];
        body.innerHTML = '';

        // Build the HTML document
        body.appendChild(buildWidget(message.widget));
    } else {
        throw `Encountered unknown message type: ${message}`;
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
