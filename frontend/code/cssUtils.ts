import { Color, Fill, TextStyle } from './models';

export function colorToCssString(color: Color): string {
    const [r, g, b, a] = color;
    return `rgba(${r * 255}, ${g * 255}, ${b * 255}, ${a})`;
}

function gradientToCssString(
    angleDegrees: number,
    stops: [Color, number][]
): string {
    let stopStrings: string[] = [];

    for (let i = 0; i < stops.length; i++) {
        let color = stops[i][0];
        let position = stops[i][1];
        stopStrings.push(`${colorToCssString(color)} ${position * 100}%`);
    }

    return `linear-gradient(${90 - angleDegrees}deg, ${stopStrings.join(
        ', '
    )})`;
}

export function fillToCssString(fill: Fill): string {
    // Solid Color
    if (fill.type === 'solid') {
        return colorToCssString(fill.color);
    }

    // Linear Gradient
    else if (fill.type === 'linearGradient') {
        if (fill.stops.length == 1) {
            return colorToCssString(fill.stops[0][0]);
        }

        return gradientToCssString(fill.angleDegrees, fill.stops);
    }

    // Image
    else if (fill.type === 'image') {
        let cssUrl = `url('${fill.imageUrl}')`;

        if (fill.fillMode == 'fit') {
            return `${cssUrl} center/contain no-repeat`;
        } else if (fill.fillMode == 'stretch') {
            return `${cssUrl} top left / 100% 100%`;
        } else if (fill.fillMode == 'tile') {
            return `${cssUrl} left top repeat`;
        } else if (fill.fillMode == 'zoom') {
            return `${cssUrl} center/cover no-repeat`;
        } else {
            // Invalid fill mode
            // @ts-ignore
            throw `Invalid fill mode for image fill: ${fill.type}`;
        }
    }

    // Invalid fill type
    // @ts-ignore
    throw `Invalid fill type: ${fill.type}`;
}

export function fillToCss(fill: Fill): { background: string } {
    return {
        background: fillToCssString(fill),
    };
}

export function textStyleToCss(
    style: 'heading1' | 'heading2' | 'heading3' | 'text' | TextStyle
): object {
    let result = {
        background: 'none',
        color: 'unset', // FIXME
    };

    // Predefined style from theme
    if (typeof style === 'string') {
        // Local values
        result['color'] = `var(--rio-global-${style}-color)`;

        // Global values
        let cssPrefix = `var(--rio-global-${style}-`;
        result['font-family'] = cssPrefix + 'font-name)';
        result['font-size'] = cssPrefix + 'font-size)';
        result['font-weight'] = cssPrefix + 'font-weight)';
        result['text-italic'] = cssPrefix + 'font-italic)';
        result['text-decoration'] = cssPrefix + 'underlined)';
        result['text-transform'] = cssPrefix + 'all-caps)';
    }

    // Explicitly defined style
    else {
        result['font-family'] = style.fontName;
        result['font-size'] = style.fontSize + 'em';
        result['font-style'] = style.italic ? 'italic' : 'normal';
        result['font-weight'] = style.fontWeight;
        result['text-decoration'] = style.underlined ? 'underline' : 'none';
        result['text-transform'] = style.allCaps ? 'uppercase' : 'none';

        // The fill could be a Color or a Fill
        if (Array.isArray(style.fill)) {
            result['color'] = colorToCssString(style.fill);
        } else {
            if (style.fill.type === 'solid') {
                result['color'] = colorToCssString(style.fill.color);
            } else {
                result['background'] = fillToCssString(style.fill);
            }
        }
    }

    return result;
}
