import { replaceChildren } from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type FlowState = ComponentState & {
    _type_: 'flow';
    children?: (number | string)[];
    spacing?: number;
};

export class FlowComponent extends ComponentBase {
    state: Required<FlowState>;

    inner: HTMLElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-flow', 'rio-zero-size-request-container');

        this.inner = document.createElement('div');
        element.appendChild(this.inner);

        return element;
    }

    updateElement(element: HTMLElement, deltaState: FlowState): void {
        // Update the children
        replaceChildren(element.id, this.inner, deltaState.children);

        // Spacing
        if (deltaState.spacing !== undefined) {
            this.inner.style.gap = `${deltaState.spacing}rem`;
        }
    }

    _updateChildLayouts(): void {}
}
