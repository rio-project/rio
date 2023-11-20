import { replaceChildrenAndResetCssProperties } from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type FlowState = ComponentState & {
    _type_: 'flow';
    children?: (number | string)[];
    spacing?: number;
};

export class FlowComponent extends ComponentBase {
    state: Required<FlowState>;

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-flow');
        return element;
    }

    _updateElement(element: HTMLElement, deltaState: FlowState): void {
        // Update the children
        replaceChildrenAndResetCssProperties(
            element.id,
            element,
            deltaState.children
        );

        // Spacing
        if (deltaState.spacing !== undefined) {
            element.style.gap = `${deltaState.spacing}rem`;
        }
    }

    _updateChildLayouts(): void {}
}
