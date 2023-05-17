import { buildWidget } from './app';
import { JsonRow } from './models';

export class RowWidget {
    static build(data: JsonRow): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-row');

        for (const child of data.children) {
            element.appendChild(buildWidget(child));
        }

        return element;
    }

    static update(element: HTMLElement, deltaState: JsonRow): void {}
}
