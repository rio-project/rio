import { fillToCss } from "./app";
import { JsonRectangle } from "./models";

export class RectangleWidget {
    static build(data: JsonRectangle): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('pygui-rectangle');
        return element;
    }

    static update(element: HTMLElement, deltaState: JsonRectangle): void {
        if (deltaState.fill !== undefined) {
            element.style.background = fillToCss(deltaState.fill);
        }

        if (deltaState.cornerRadius !== undefined) {
            const [topLeft, topRight, bottomRight, bottomLeft] =
                deltaState.cornerRadius;
            element.style.borderRadius = `${topLeft}em ${topRight}em ${bottomRight}em ${bottomLeft}em`;
        }
    }
}