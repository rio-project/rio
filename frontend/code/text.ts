import { TextStyle } from './models';
import { colorToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type TextState = WidgetState & {
    text?: string;
    multiline?: boolean;
    style?: 'heading1' | 'heading2' | 'heading3' | 'text' | TextStyle;
};

function getTextStyleValues(
    style: 'heading1' | 'heading2' | 'heading3' | 'text' | TextStyle
): object {
    let result = {};

    // Predefined style from theme
    if (typeof style === 'string') {
        let textOrHeading = style === 'text' ? 'text' : 'heading';

        // Local values
        result['color'] = `var(--rio-local-${textOrHeading}-color)`;

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
        result['color'] = colorToCss(style.fontColor);
        result['font-size'] = style.fontSize + 'em';
        result['font-style'] = style.italic ? 'italic' : 'normal';
        result['font-weight'] = style.fontWeight;
        result['text-decoration'] = style.underlined ? 'underline' : 'none';
        result['text-transform'] = style.allCaps ? 'uppercase' : 'none';
    }

    return result;
}

export class TextWidget extends WidgetBase {
    state: Required<TextState>;

    createElement(): HTMLElement {
        let containerElement = document.createElement('div');
        containerElement.classList.add('rio-text');

        let textElement = document.createElement('div');
        containerElement.appendChild(textElement);
        return containerElement;
    }

    updateElement(containerElement: HTMLElement, deltaState: TextState): void {
        let textElement = containerElement.firstElementChild as HTMLElement;

        if (deltaState.text !== undefined) {
            textElement.innerText = deltaState.text;
        }

        if (deltaState.multiline !== undefined) {
            textElement.style.whiteSpace = deltaState.multiline
                ? 'normal'
                : 'nowrap';
        }

        // Text style: No change
        if (deltaState.style !== undefined) {
            let styleValues = getTextStyleValues(deltaState.style);
            Object.assign(textElement.style, styleValues);
        }
    }
}
