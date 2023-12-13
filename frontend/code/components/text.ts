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

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-text');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: TextState): void {
        // Text content
        //
        // Make sure not to allow any linebreaks if the text is not multiline.
        if (deltaState.text !== undefined) {
            element.innerText = deltaState.text.replace(/\n/g, ' ');
        }

        // Multiline
        if (deltaState.multiline !== undefined) {
            element.style.whiteSpace = deltaState.multiline
                ? 'pre-wrap'
                : 'pre';
        }

        // Selectable
        if (deltaState.selectable !== undefined) {
            element.style.userSelect = deltaState.selectable ? 'text' : 'none';
        }

        // Text style
        if (deltaState.style !== undefined) {
            Object.assign(element.style, textStyleToCss(deltaState.style));
        }
    }

    updateRequestedWidth(): void {
        this.requestedWidth = 50;
    }

    updateRequestedHeight(): void {
        this.requestedHeight = 30;
    }
}
