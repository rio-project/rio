import { ColorSetOrNull, Fill } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { applyFillToSVG } from '../designApplication';
import { pixelsPerEm } from '../app';

export type IconState = ComponentState & {
    svgSource: string;
    fill: Fill | ColorSetOrNull | 'keep';
};

function createSVGPath(
    div: HTMLElement,
    svgSource: string,
    fill: Fill | ColorSetOrNull
) {
    // Create an SVG element
    div.innerHTML = svgSource;
    let svgRoot = div.firstChild as SVGSVGElement;

    // If not fill was provided, use the default foreground color.
    if (fill === null) {
        svgRoot.style.fill = 'var(--rio-local-text-color)';
        return;
    }

    // If the fill is a string apply the appropriate theme color.
    if (typeof fill === 'string') {
        svgRoot.style.fill = `var(--rio-global-${fill}-fg)`;
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

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-icon', 'rio-zero-size-request-container');
        return element;
    }

    _updateElement(element: HTMLElement, deltaState: IconState): void {
        // Remove all children
        element.innerHTML = '';

        // Add the SVG
        createSVGPath(
            element,
            deltaState.svgSource,
            deltaState.fill === 'keep' ? null : deltaState.fill
        );

        // Size
        //
        // The SVG has no size on it's own. This is so it scales up, rather than
        // staying a fixed size. However, this removes it's "size request". If a
        // size was provided by the backend, apply that explicitly.
        //
        // TODO / FIXME: Shouldn't this account for the aspect ratio?
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
