import { replaceChildren } from './app';
import { JsonRow } from './models';

export class RowWidget {
    static build(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-row');
        return element;
    }

    static update(element: HTMLElement, deltaState: JsonRow): void {
        replaceChildren(element, deltaState.children);
    }
}
