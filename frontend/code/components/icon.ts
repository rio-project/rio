import { ColorSet, Fill } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { applyFillToSVG } from '../designApplication';
import { pixelsPerEm } from '../app';

export type IconState = ComponentState & {
    svgSource: string;
    fill: Fill | ColorSet | 'dim';
};

function createSVGPath(
    div: HTMLElement,
    svgSource: string,
    fill: Fill | ColorSet | 'dim'
): void {
    // Create an SVG element
    div.innerHTML = svgSource;
    let svgRoot = div.firstChild as SVGSVGElement;

    // If no fill was provided, use the default foreground color.
    if (fill === 'keep') {
        svgRoot.style.fill = 'var(--rio-local-text-color)';
        return;
    }

    // "dim" is a special case, which is represented by using the "neutral"
    // style, but with a reduced opacity.
    if (fill === 'dim') {
        svgRoot.style.fill = `var(--rio-global-neutral-fg)`;
        svgRoot.style.opacity = '0.4';
        return;
    }

    // If the fill is a string apply the appropriate theme color. Note that this
    // uses the background rather than foreground color. The foreground is
    // intended to be used if the background was already set to background
    // color.
    svgRoot.style.removeProperty('opacity');

    if (typeof fill === 'string') {
        svgRoot.style.fill = `var(--rio-global-${fill}-bg)`;
        return;
    }

    // If the fill is a color convert it to a solid fill first.
    if (Array.isArray(fill)) {
        fill = {
            type: 'solid',
            // @ts-ignore
            color: fill,
        };
    }

    // Apply the fill
    // @ts-ignore
    applyFillToSVG(svgRoot, fill);
}

export class IconComponent extends ComponentBase {
    state: Required<IconState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-icon', 'rio-zero-size-request-container');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: IconState): void {
        // Remove all children
        element.innerHTML = '';

        // Add the SVG
        createSVGPath(element, deltaState.svgSource, deltaState.fill);

        // Size
        //
        // The SVG has no size on its own. This is so it scales up, rather than
        // staying a fixed size. However, this removes its "size request". If a
        // size was provided by the backend, apply that explicitly.
        if (deltaState._size_ !== undefined) {
            let [width, height] = deltaState._size_;
            let svgElement = element.firstElementChild as SVGSVGElement;

            // SVG can't handle `rem`, but needs `px`. Convert.
            svgElement.setAttribute(
                'width',
                width === null ? '100%' : `${width * pixelsPerEm}px`
            );
            svgElement.setAttribute(
                'height',
                height === null ? '100%' : `${height * pixelsPerEm}px`
            );
        }
    }
}
