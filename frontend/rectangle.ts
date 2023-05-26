import { colorToCss, fillToCss, replaceOnlyChild } from './app';
import { JsonRectangle } from './models';

export class RectangleWidget {
    static build(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-rectangle');
        return element;
    }

    static update(element: HTMLElement, deltaState: JsonRectangle): void {
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
