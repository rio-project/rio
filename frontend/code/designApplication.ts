import { Color, ColorSet, Fill } from './models';
import { colorToCssString } from './cssUtils';

export function applyColorSet(element: HTMLElement, colorSet: ColorSet): void {
    // Remove all switcheroos
    element.classList.remove(
        'rio-switcheroo-primary',
        'rio-switcheroo-secondary',
        'rio-switcheroo-background',
        'rio-switcheroo-neutral',
        'rio-switcheroo-disabled',
        'rio-switcheroo-success',
        'rio-switcheroo-warning',
        'rio-switcheroo-danger',
        'rio-switcheroo-custom',
        'rio-switcheroo-accent-to-plain'
    );

    // If no colorset is desired don't apply any new one
    if (colorSet === 'keep') {
        return;
    }

    // Otherwise find and apply the correct switcheroo
    let switcheroo: string;

    // Is this a color instance?
    if (typeof colorSet !== 'string') {
        // Expose the color as CSS variables
        element.style.setProperty(
            '--rio-local-custom-bg',
            colorToCssString(colorSet.background)
        );
        element.style.setProperty(
            '--rio-local-custom-fg',
            colorToCssString(colorSet.foreground)
        );

        // Select the custom switcheroo
        switcheroo = 'custom';
    } else {
        switcheroo = colorSet;
    }

    // Add the new switcheroo
    element.classList.add(`rio-switcheroo-${switcheroo}`);
}

export function applyFillToSVG(svgRoot: SVGSVGElement, fill: Fill): void {
    switch (fill.type) {
        case 'solid':
            applySolidFill(svgRoot, fill.color);
            break;

        case 'linearGradient':
            applyLinearGradientFill(svgRoot, fill.angleDegrees, fill.stops);
            break;

        case 'image':
            applyImageFill(svgRoot, fill.imageUrl, fill.fillMode);
            break;

        default:
            throw new Error(`Invalid fill type: ${fill}`);
    }
}

function applySolidFill(svgRoot: SVGSVGElement, color: Color): void {
    const [r, g, b, a] = color;
    svgRoot.style.fill = `rgba(${r * 255}, ${g * 255}, ${b * 255}, ${a})`;
}

function applyLinearGradientFill(
    svgRoot: SVGSVGElement,
    angleDegrees: number,
    stops: [Color, number][]
): void {
    // Create a new linear gradient
    const gradientId = generateUniqueId();
    const gradient = createLinearGradient(gradientId, angleDegrees, stops);

    // Add it to the "defs" section of the SVG
    let defs = svgRoot.querySelector('defs');

    if (defs === null) {
        defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        svgRoot.appendChild(defs);
    }

    defs.appendChild(gradient);

    // Add the gradient to the path
    svgRoot.style.fill = `url(#${gradientId})`;
}

function applyImageFill(
    svgRoot: SVGSVGElement,
    imageUrl: string,
    fillMode: 'fit' | 'stretch' | 'tile' | 'zoom'
): void {
    // Create a pattern
    const patternId = generateUniqueId();
    const pattern = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'pattern'
    );
    pattern.setAttribute('id', patternId);
    pattern.setAttribute('width', '100%');
    pattern.setAttribute('height', '100%');
    pattern.setAttribute('preserveAspectRatio', 'none');

    // Create an image
    const image = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'image'
    );
    image.setAttribute('width', '100%');
    image.setAttribute('height', '100%');
    image.setAttribute('href', imageUrl);
    image.setAttribute('preserveAspectRatio', 'none');
    pattern.appendChild(image);

    // Add the pattern to the "defs" section of the SVG
    let defs = svgRoot.querySelector('defs');

    if (defs === null) {
        defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        svgRoot.appendChild(defs);
    }

    defs.appendChild(pattern);

    // Apply the pattern to the path
    svgRoot.setAttribute('fill', `url(#${patternId})`);
}

function generateUniqueId(): string {
    return Math.random().toString(36);
}

function createLinearGradient(
    gradientId: string,
    angleDegrees: number,
    stops: [Color, number][]
): SVGLinearGradientElement {
    const gradient = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'linearGradient'
    );
    gradient.setAttribute('id', gradientId);
    gradient.setAttribute('gradientTransform', `rotate(${angleDegrees})`);

    let ii = -1;
    for (const [color, offset] of stops) {
        ii += 1;

        const [r, g, b, a] = color;
        const stop = document.createElementNS(
            'http://www.w3.org/2000/svg',
            'stop'
        );

        stop.setAttribute('offset', `${offset}`);
        stop.setAttribute(
            'style',
            `stop-color: rgba(${r * 255}, ${g * 255}, ${b * 255}, ${a})`
        );
        stop.setAttribute('id', `${gradientId}-stop-${ii}`);
        gradient.appendChild(stop);
    }

    return gradient;
}

/// Given an element, load the icon with the given name and apply it to the
/// element.
///
/// The element's size is not affected. Make it however big you want the icon
/// to be. Any children of the element will be removed.
export async function applyIcon(
    target: HTMLElement,
    iconName: string,
    cssColor: string
): Promise<void> {
    // Load the icon
    //
    // TODO: Cache the icons, so the same icon isn't loaded multiple times.
    let iconUrl = `/rio/icon/${iconName}`;
    let response = await fetch(iconUrl);
    let svgSource = await response.text();

    // Create the SVG element
    target.innerHTML = svgSource;

    // Apply the color
    let svgRoot = target.querySelector('svg') as SVGSVGElement;
    svgRoot.style.fill = cssColor;
}
