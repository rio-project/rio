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
        let containerElement = document.createElement('div');
        containerElement.classList.add('reflex-text');

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

        if (deltaState.style !== undefined) {
            const style = deltaState.style;
            textElement.style.fontFamily = style.fontName;
            textElement.style.color = colorToCss(style.fontColor);
            textElement.style.fontSize = style.fontSize + 'em';
            textElement.style.fontStyle = style.italic ? 'italic' : 'normal';
            textElement.style.fontWeight = style.fontWeight;
            textElement.style.textDecoration = style.underlined
                ? 'underline'
                : 'none';
            textElement.style.textTransform = style.allCaps
                ? 'uppercase'
                : 'none';
        }
    }
}
