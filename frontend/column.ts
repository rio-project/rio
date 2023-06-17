import { replaceChildren } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

type ColumnState = WidgetState & {
    _type_: 'column';
    children?: number[];
    spacing?: number;
};

export class ColumnWidget extends WidgetBase {
    createInnerElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-column');
        return element;
    }

    updateInnerElement(element: HTMLElement, deltaState: ColumnState): void {
        replaceChildren(element, deltaState.children);

        if (deltaState.spacing !== undefined) {
            element.style.gap = `${deltaState.spacing}em`;
        }
    }
}
