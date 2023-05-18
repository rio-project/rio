import { replaceChildren } from './app';
import { JsonColumn } from './models';

export class ColumnWidget {
    static build(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-column');

        return element;
    }

    static update(element: HTMLElement, deltaState: JsonColumn): void {
        replaceChildren(element, deltaState.children);
    }
}
