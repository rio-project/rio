import { replaceChildren } from './app';
import { WidgetState } from './widgetBase';

export type RowState = WidgetState & {
    _type_: 'row';
    children?: number[];
    spacing?: number;
};

export class RowWidget {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-row');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: RowState): void {
        replaceChildren(element, deltaState.children);

        if (deltaState.spacing !== undefined) {
            element.style.gap = `${deltaState.spacing}rem`;
        }
    }
}
