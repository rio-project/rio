import { Color, ColorSpec, Fill } from './models';

export function applyColorSpec(element: HTMLElement, color: ColorSpec): void {
    let switcheroo;

    // Is this a color instance?
    if (typeof color !== 'string') {
        // Expose the color as CSS variables
        element.style.setProperty(
            '--reflex-local-custom-color',
            colorToCss(color.color)
        );
        element.style.setProperty(
            '--reflex-local-custom-color-variant',
            colorToCss(color.colorVariant)
        );
        element.style.setProperty(
            '--reflex-local-custom-color-variant',
            colorToCss(color.textColor)
        );

        // Select the custom switcheroo
        switcheroo = 'custom';
    } else {
        switcheroo = color;
    }

    // Remove all switcheroos
    element.classList.remove(
        'reflex-switcheroo-primary',
        'reflex-switcheroo-accent',
        'reflex-switcheroo-success',
        'reflex-switcheroo-warning',
        'reflex-switcheroo-danger',
        'reflex-switcheroo-custom',
        'reflex-switcheroo-disabled'
    );

    // Add the new switcheroo
    element.classList.add(`reflex-switcheroo-${switcheroo}`);
}

export function colorToCss(color: Color): string {
    const [r, g, b, a] = color;

    const red = Math.round(r * 255)
        .toString(16)
        .padStart(2, '0');

    const green = Math.round(g * 255)
        .toString(16)
        .padStart(2, '0');

    const blue = Math.round(b * 255)
        .toString(16)
        .padStart(2, '0');

    const alpha = Math.round(a * 255)
        .toString(16)
        .padStart(2, '0');

    return `#${red}${green}${blue}${alpha}`;
}

export function applyFillToSVG(
    svgRoot: SVGSVGElement,
    svgPath: SVGPathElement,
    fill: Fill
): void {
    switch (fill.type) {
        case 'solid':
            applySolidFill(svgPath, fill.color);
            break;

        case 'linearGradient':
            applyLinearGradientFill(
                svgRoot,
                svgPath,
                fill.angleDegrees,
                fill.stops
            );
            break;

        case 'image':
            applyImageFill(svgRoot, svgPath, fill.imageUrl, fill.fillMode);
            break;
    }
}

function applySolidFill(svgElement: SVGPathElement, color: Color): void {
    const [r, g, b, a] = color;
    svgElement.style.fill = `rgba(${r * 255}, ${g * 255}, ${b * 255}, ${a})`;
}

function applyLinearGradientFill(
    svgRoot: SVGSVGElement,
    svgPath: SVGPathElement,
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
    svgPath.style.fill = `url(#${gradientId})`;
}

function applyImageFill(
    svgRoot: SVGSVGElement,
    svgPath: SVGPathElement,
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
    svgPath.setAttribute('fill', `url(#${patternId})`);
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
