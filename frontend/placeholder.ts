import { fillToCss, replaceOnlyChild } from './app';
import { JsonPlaceholder, JsonRectangle } from './models';

export class PlaceholderWidget {
    static build(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    static update(element: HTMLElement, deltaState: JsonPlaceholder): void {
        replaceOnlyChild(element, deltaState._child_);
    }
}
