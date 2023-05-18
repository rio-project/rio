import { replaceOnlyChild } from './app';
import { JsonPlaceholder } from './models';

export class PlaceholderWidget {
    static build(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    static update(element: HTMLElement, deltaState: JsonPlaceholder): void {
        replaceOnlyChild(element, deltaState._child_);
    }
}
