import { colorToCss, fillToCss, replaceOnlyChild } from './app';
import { BoxStyle } from './models';
import { WidgetBase, WidgetState } from './widgetBase';

export type RectangleState = WidgetState & {
    _type_: 'rectangle';
    style?: BoxStyle;
    child?: number;
    hover_style?: BoxStyle | null;
    transition_time?: number;
};

function setBoxStyleVariables(
    element: HTMLElement,
    style: BoxStyle | undefined,
    prefix: string,
    suffix: string
): void {
    // Do nothing if no style was passed
    if (style === undefined) {
        return;
    }

    // Define a set of CSS variables which should be set. For now without the
    // prefix
    let variables: object = {};

    if (style === null) {
        variables = {
            background: 'transparent',

            'stroke-color': 'transparent',
            'stroke-width': '0rem',

            'corner-radius-top-left': '0rem',
            'corner-radius-top-right': '0rem',
            'corner-radius-bottom-right': '0rem',
            'corner-radius-bottom-left': '0rem',

            'shadow-color': 'transparent',
            'shadow-radius': '0rem',
            'shadow-offset-x': '0rem',
            'shadow-offset-y': '0rem',
        };
    } else {
        variables['background'] = fillToCss(style.fill);

        variables['stroke-color'] = colorToCss(style.strokeColor);
        variables['stroke-width'] = `${style.strokeWidth}rem`;

        variables['corner-radius-top-left'] = `${style.cornerRadius[0]}rem`;
        variables['corner-radius-top-right'] = `${style.cornerRadius[1]}rem`;
        variables['corner-radius-bottom-right'] = `${style.cornerRadius[2]}rem`;
        variables['corner-radius-bottom-left'] = `${style.cornerRadius[3]}rem`;

        variables['shadow-color'] = colorToCss(style.shadowColor);
        variables['shadow-radius'] = `${style.shadowRadius}rem`;
        variables['shadow-offset-x'] = `${style.shadowOffset[0]}rem`;
        variables['shadow-offset-y'] = `${style.shadowOffset[1]}rem`;
    }

    // Set the variables and add the prefix
    for (const [key, value] of Object.entries(variables)) {
        element.style.setProperty(`--${prefix}${key}${suffix}`, value);
    }
}

export class RectangleWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-rectangle');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: RectangleState): void {
        replaceOnlyChild(element, deltaState.child);

        setBoxStyleVariables(element, deltaState.style, 'rectangle-', '');

        if (deltaState.transition_time !== undefined) {
            element.style.transitionDuration = `${deltaState.transition_time}s`;
        }

        if (deltaState.hover_style === null) {
            element.classList.remove('reflex-rectangle-hover');
        } else if (deltaState.hover_style !== undefined) {
            element.classList.add('reflex-rectangle-hover');
            setBoxStyleVariables(
                element,
                deltaState.hover_style,
                'rectangle-',
                '-hover'
            );
        }
    }
}
