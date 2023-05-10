import { TextWidget } from './text';
import { RowWidget } from './row';
import { ColumnWidget } from './column';
import { RectangleWidget } from './rectangle';
import { StackWidget } from './stack';
import { MarginWidget } from './margin';
import { AlignWidget } from './align';
import { Color, Fill, JsonWidget } from './models';

// @ts-ignore
const initialRootWidget: JsonWidget = '{root_widget}';

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
    // Make sure the widget type is valid
    const widgetClass = widgetClasses[widget.type]!;

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


function main() {
    // Build the HTML document
    let body = document.getElementsByTagName('body')[0];
    body.appendChild(buildWidget(initialRootWidget));
}

main();
