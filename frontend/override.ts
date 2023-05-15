import { buildWidget } from './app';
import { JsonOverride } from './models';

export class OverrideWidget {
    static build(data: JsonOverride): HTMLElement {
        let element = document.createElement('div');
        element.appendChild(buildWidget(data.child));
        return element;
    }

    static update(element: HTMLElement, deltaState: JsonOverride): void {

        if (deltaState.width !== undefined) {
            if (deltaState.width === null) {
                element.style.removeProperty('width');
            } else {
                element.style.width = `${deltaState.width}em`;
            }
        }

        if (deltaState.height !== undefined) {
            if (deltaState.height === null) {
                element.style.removeProperty('height');
            } else {
                element.style.height = `${deltaState.height}em`;
            }
        }
    }
}
