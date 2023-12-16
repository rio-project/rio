import { TextStyle } from '../models';
import { textStyleToCss } from '../cssUtils';
import { ComponentBase, ComponentState } from './componentBase';
import { LayoutContext } from '../layouting';
import { pixelsPerEm } from '../app';
import { getTextDimensions } from '../layoutHelpers';

// TODO

export type TextState = ComponentState & {
    text?: string;
    multiline?: boolean;
    selectable?: boolean;
    style?: 'heading1' | 'heading2' | 'heading3' | 'text' | 'dim' | TextStyle;
};

export class TextComponent extends ComponentBase {
    state: Required<TextState>;

    private inner: HTMLElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-text');

        this.inner = document.createElement('div');
        element.appendChild(this.inner);

        return element;
    }

    updateElement(element: HTMLElement, deltaState: TextState): void {
        // Text content
        //
        // Make sure not to allow any linebreaks if the text is not multiline.
        if (deltaState.text !== undefined) {
            this.inner.textContent = deltaState.text.replace(/\n/g, ' ');
        }

        // Multiline
        if (deltaState.multiline !== undefined) {
            this.inner.style.whiteSpace = deltaState.multiline
                ? 'pre-wrap'
                : 'pre';
        }

        // Selectable
        if (deltaState.selectable !== undefined) {
            this.inner.style.userSelect = deltaState.selectable
                ? 'text'
                : 'none';
        }

        // Text style
        if (deltaState.style !== undefined) {
            Object.assign(this.inner.style, textStyleToCss(deltaState.style));
        }

        this.makeLayoutDirty();
    }

    updateRequestedWidth(ctx: LayoutContext): void {
        if (this.state.multiline) {
            // TODO: Consider the min content width? It likely wouldn't have
            // much of an effect but slow everything down.
            this.requestedWidth = 0;
        } else {
            [this.requestedWidth, this.requestedHeight] = getTextDimensions(
                this.state.text,
                this.state.style
            );
        }
        console.log(
            `REQUESTING: ${this.requestedWidth}  ${this.inner.textContent}  ${this.state.multiline}`
        );
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        // Wrong, if the text is hidden
        this.requestedHeight = this.inner.scrollHeight / pixelsPerEm;
    }
}
