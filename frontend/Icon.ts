import { Fill } from './models';
import { colorToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type IconState = WidgetState & {
    iconPath: Array<[number, number]>;
    fill: Fill;
};

function createSVGPath(div, bezierPoints, fill) {
    // Create an SVG element
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100');
    svg.setAttribute('height', '100');

    // Create an SVG path
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');

    // Construct the path data using the Bezier control points
    const pathData =
        `M${bezierPoints[0][0]} ${bezierPoints[0][1]} ` +
        `C${bezierPoints
            .slice(1)
            .map((point) => point.join(' '))
            .join(', ')}`;

    // Set attributes for the path
    path.setAttribute('d', pathData);
    path.setAttribute('fill', fill);

    // Append the path to the SVG
    svg.appendChild(path);

    // Append the SVG to the provided div element
    div.appendChild(svg);
}

export class IconWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-icon');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: IconState): void {
        // Remove all children
        element.innerHTML = '';

        // Add the SVG
        createSVGPath(element, deltaState.iconPath, deltaState.fill);
    }
}
