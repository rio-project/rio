import { Color } from './models';
import { colorToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type TextState = WidgetState & {
    text?: string;
    multiline?: boolean;
    font?: string;
    font_color?: Color;
    font_size?: number;
    font_weight?: string;
    italic?: boolean;
    underlined?: boolean;
};

export class TextWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-text');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: TextState): void {
        if (deltaState.text !== undefined) {
            element.innerText = deltaState.text;
        }

        if (deltaState.multiline !== undefined) {
            element.style.whiteSpace = deltaState.multiline
                ? 'normal'
                : 'nowrap';
        }

        if (deltaState.font !== undefined) {
            element.style.fontFamily = deltaState.font;
        }

        if (deltaState.font_color !== undefined) {
            element.style.color = colorToCss(deltaState.font_color);
        }

        if (deltaState.font_size !== undefined) {
            element.style.fontSize = deltaState.font_size + 'rem';
        }

        if (deltaState.font_weight !== undefined) {
            element.style.fontWeight = deltaState.font_weight;
        }

        if (deltaState.italic !== undefined) {
            element.style.fontStyle = deltaState.italic ? 'italic' : 'normal';
        }

        if (deltaState.underlined !== undefined) {
            element.style.textDecoration = deltaState.underlined
                ? 'underline'
                : 'none';
        }
    }
}
