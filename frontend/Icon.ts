import { ColorSet, Fill } from './models';
import { WidgetBase, WidgetState } from './widgetBase';
import { applyFillToSVG } from './design_application';

export type IconState = WidgetState & {
    svgSource: string;
    fill: Fill | ColorSet;
};

function createSVGPath(
    div: HTMLElement,
    svgSource: string,
    fill: Fill | ColorSet
) {
    // Create an SVG element
    div.innerHTML = svgSource;
    let svgRoot = div.firstChild as    SVGSVGElement;

    // Apply the style
    applyFillToSVG(svgRoot, fill);
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
            deltaState.svgSource,
            deltaState.fill
        );
    }
}
