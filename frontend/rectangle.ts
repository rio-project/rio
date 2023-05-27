import { colorToCss, fillToCss, replaceOnlyChild } from './app';
import { Color, Fill } from './models';
import { WidgetBase, WidgetState } from './widgetBase';

export type RectangleState = WidgetState & {
    _type_: 'rectangle';
    fill?: Fill;
    child?: number;
    corner_radius?: [number, number, number, number];
    stroke_width?: number;
    stroke_color?: Color;
};

export class RectangleWidget extends WidgetBase  {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-rectangle');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: RectangleState): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.fill !== undefined) {
            element.style.background = fillToCss(deltaState.fill);
        }

        if (deltaState.corner_radius !== undefined) {
            const [topLeft, topRight, bottomRight, bottomLeft] =
                deltaState.corner_radius;
            element.style.borderRadius = `${topLeft}rem ${topRight}rem ${bottomRight}rem ${bottomLeft}rem`;
        }

        if (deltaState.stroke_width !== undefined) {
            element.style.borderWidth = `${deltaState.stroke_width}rem`;
        }

        if (deltaState.stroke_color !== undefined) {
            if (deltaState.stroke_color === null) {
                element.style.borderColor = 'transparent';
            } else {
                element.style.borderColor = colorToCss(deltaState.stroke_color);
            }
        }
    }
}
