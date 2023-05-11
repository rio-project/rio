import { TextWidget } from './text';
import { RowWidget } from './row';
import { ColumnWidget } from './column';
import { RectangleWidget } from './rectangle';
import { StackWidget } from './stack';
import { MarginWidget } from './margin';
import { AlignWidget } from './align';
import { Color, Fill, JsonWidget } from './models';
import WebSocket = require('ws');

const initialMessages = '{initial_messages}';
let ws: WebSocket = null;

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
    text: TextWidget,
    row: RowWidget,
    column: ColumnWidget,
    rectangle: RectangleWidget,
    stack: StackWidget,
    margin: MarginWidget,
    align: AlignWidget,
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
    result.id = 'pygui-id-' + widget.id;

    // Store the widget's type in the element. This is used by the update
    // function to determine the correct update function to call.
    result.setAttribute('data-pygui-type', widget.type);

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
    }
}

function main() {
    // Process initial messages
    console.log(`Processing ${initialMessages.length} initial message(s)`)
    for (let message of initialMessages) {
        processMessage(message);
    }

    // Connect to the websocket
    var url = new URL('/ws', window.location.href);
    url.protocol = url.protocol.replace('http', 'ws');
    console.log(`Connecting websocket to ${url.href}`)

    // ws = new WebSocket(url.href);
    ws = new WebSocket("ws://localhost:8000/ws");

    ws.addEventListener('open', onOpen);
    ws.addEventListener('message', onMessage);
    ws.addEventListener('error', onError);
    ws.addEventListener('close', onClose);
}

function onOpen() {
    console.log('Connection opened');
}

function onMessage(event: WebSocket.MessageEvent) {
    console.log(`Received message: ${event.data}`);
}

function onError(event: WebSocket.ErrorEvent) {
    console.log(`Error: ${event.message}`);
}

function onClose(event: WebSocket.CloseEvent) {
    console.log(`Connection closed: ${event.reason}`);
}

// main();

let ws = new WebSocket("ws://localhost:{self.port}/ws");
