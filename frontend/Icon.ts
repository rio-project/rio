import { Fill } from './models';
import { fillToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';
import { applyFillToSVG } from './design_application';

export type IconState = WidgetState & {
    width: number;
    height: number;
    path: string;
    fill: Fill;
};

function createSVGPath(
    div: HTMLElement,
    width: number,
    height: number,
    path: string,
    fill: Fill
) {
    // Create an SVG element
    const svgRoot = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'svg'
    );
    svgRoot.setAttribute('viewBox', `0 0 ${width} ${height}`);

    // Create an SVG path
    const svgPath = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'path'
    );

    svgPath.setAttribute('d', path);

    // Apply the style
    applyFillToSVG(svgRoot, svgPath, fill);

    // Append the path to the SVG
    svgRoot.appendChild(svgPath);

    // Append the SVG to the provided div element
    div.appendChild(svgRoot);
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
        createSVGPath(
            element,
            deltaState.width,
            deltaState.height,
            deltaState.path,
            deltaState.fill
        );
    }
}
