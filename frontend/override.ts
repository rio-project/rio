import { replaceOnlyChild } from './app';
import { JsonOverride } from './models';

export class OverrideWidget {
    static build(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    static update(element: HTMLElement, deltaState: JsonOverride): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.width !== undefined) {
            if (deltaState.width === null) {
                element.style.removeProperty('width');
            } else {
                element.style.width = `${deltaState.width}rem`;
            }
        }

        if (deltaState.height !== undefined) {
            if (deltaState.height === null) {
                element.style.removeProperty('height');
            } else {
                element.style.height = `${deltaState.height}rem`;
            }
        }
    }
}
