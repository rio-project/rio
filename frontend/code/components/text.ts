import { TextStyle } from '../models';
import { textStyleToCss } from '../cssUtils';
import { ComponentBase, ComponentState } from './componentBase';

export type TextState = ComponentState & {
    text?: string;
    multiline?: boolean;
    style?: 'heading1' | 'heading2' | 'heading3' | 'text' | TextStyle;
};

export class TextComponent extends ComponentBase {
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
            let styleValues = textStyleToCss(deltaState.style);
            Object.assign(textElement.style, styleValues);
        }
    }
}
