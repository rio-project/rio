import { colorToCss, fillToCss, replaceOnlyChild } from './app';
import { BoxStyle } from './models';
import { WidgetBase, WidgetState } from './widgetBase';

export type RectangleState = WidgetState & {
    _type_: 'rectangle';
    style?: BoxStyle;
    child?: number;
};

export class RectangleWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-rectangle');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: RectangleState): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.style !== undefined) {
            const style = deltaState.style;

            element.style.background = fillToCss(style.fill);

            element.style.borderWidth = `${style.strokeWidth}rem`;

            element.style.borderColor = colorToCss(style.strokeColor);

            const [topLeft, topRight, bottomRight, bottomLeft] =
                style.cornerRadius;
            element.style.borderRadius = `${topLeft}rem ${topRight}rem ${bottomRight}rem ${bottomLeft}rem`;
        }
    }
}
