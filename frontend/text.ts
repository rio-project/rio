import { TextStyle } from './models';
import { colorToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type TextState = WidgetState & {
    text?: string;
    multiline?: boolean;
    style?: TextStyle;
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

        if (deltaState.style !== undefined) {
            const style = deltaState.style;
            element.style.fontFamily = style.fontName;
            element.style.color = colorToCss(style.fontColor);
            element.style.fontSize = style.fontSize + 'rem';
            element.style.fontStyle = style.italic ? 'italic' : 'normal';
            element.style.fontWeight = style.fontWeight;
            element.style.textDecoration = style.underlined
                ? 'underline'
                : 'none';
            element.style.textTransform = style.allCaps ? 'uppercase': 'none';
        }
    }
}
