import { TextStyle } from '../models';
import { textStyleToCss } from '../cssUtils';
import { ComponentBase, ComponentState } from './componentBase';

export type TextState = ComponentState & {
    text?: string;
    multiline?: boolean;
    selectable?: boolean;
    style?: 'heading1' | 'heading2' | 'heading3' | 'text' | 'dim' | TextStyle;
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
        //
        // Make sure not to allow any linebreaks if the text is not multiline.
        if (deltaState.text !== undefined) {
            textElement.innerText = deltaState.text.replace(/\n/g, ' ');
        }

        // Multiline
        if (deltaState.multiline !== undefined) {
            textElement.style.whiteSpace = deltaState.multiline
                ? 'pre-wrap'
                : 'pre';
        }

        // Selectable
        if (deltaState.selectable !== undefined) {
            textElement.style.userSelect = deltaState.selectable
                ? 'text'
                : 'none';
        }

        // Text style
        if (deltaState.style !== undefined) {
            Object.assign(textElement.style, textStyleToCss(deltaState.style));
        }
    }
}
