import { TextStyle } from '../models';
import { textStyleToCss } from '../cssUtils';
import { ComponentBase, ComponentState } from './componentBase';

export type TextState = ComponentState & {
    text?: string;
    multiline?: boolean;
    selectable?: boolean;
    style?: 'heading1' | 'heading2' | 'heading3' | 'text' | TextStyle;
};

export class TextComponent extends ComponentBase {
    state: Required<TextState>;

    _createElement(): HTMLElement {
        let containerElement = document.createElement('div');
        containerElement.classList.add('rio-text');

        let textElement = document.createElement('div');
        containerElement.appendChild(textElement);
        return containerElement;
    }

    _updateElement(containerElement: HTMLElement, deltaState: TextState): void {
        let textElement = containerElement.firstElementChild as HTMLElement;

        // Text content
        if (deltaState.text !== undefined) {
            textElement.innerText = deltaState.text;
        }

        // Multiline
        if (deltaState.multiline !== undefined) {
            textElement.style.whiteSpace = deltaState.multiline
                ? 'normal'
                : 'nowrap';
        }

        // Selectable
        if (deltaState.selectable !== undefined) {
            textElement.style.userSelect = deltaState.selectable
                ? 'text'
                : 'none';
        }

        // Text style
        if (deltaState.style !== undefined) {
            let styleValues = textStyleToCss(deltaState.style);
            Object.assign(textElement.style, styleValues);
        }
    }
}
