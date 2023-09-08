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
    let svgRoot = div.firstChild as SVGSVGElement;

    svgRoot.style.width = '100%';
    svgRoot.style.height = '100%';

    // Preprocess the style

    // If the fill is a color convert it to a solid fill first.
    if (Array.isArray(fill)) {
        fill = {
            type: 'solid',

            // @ts-ignore
            color: fill,
        };
    }

    // If the fill is a string apply the appropriate theme color.
    else if (typeof fill === 'string') {
        console.log('TODO: Support theme colors for `Icon` widgets');
        fill = {
            type: 'solid',
            color: [1, 0, 1, 1],
        };
    }

    // Apply it
    // @ts-ignore
    applyFillToSVG(svgRoot, fill);
}

export class IconWidget extends WidgetBase {
    state: Required<IconState>;
    
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-icon');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: IconState): void {
        // Remove all children
        element.innerHTML = '';

        // Add the SVG
        createSVGPath(element, deltaState.svgSource, deltaState.fill);
    }
}
