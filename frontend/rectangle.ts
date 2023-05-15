import { buildWidget, fillToCss } from './app';
import { JsonRectangle } from './models';

export class RectangleWidget {
    static build(data: JsonRectangle): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('pygui-rectangle');

        if (data.child !== undefined && data.child !== null) {
            element.appendChild(buildWidget(data.child));
        }

        return element;
    }

    static update(element: HTMLElement, deltaState: JsonRectangle): void {
        if (deltaState.fill !== undefined) {
            element.style.background = fillToCss(deltaState.fill);
        }

        if (deltaState.corner_radius !== undefined) {
            const [topLeft, topRight, bottomRight, bottomLeft] =
                deltaState.corner_radius;
            element.style.borderRadius = `${topLeft}em ${topRight}em ${bottomRight}em ${bottomLeft}em`;
        }
    }
}
