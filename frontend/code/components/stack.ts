import {
    getInstanceByComponentId,
    replaceChildren,
} from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type StackState = ComponentState & {
    _type_: 'stack';
    children?: number[];
};

export class StackComponent extends ComponentBase {
    state: Required<StackState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-stack');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: StackState): void {
        replaceChildren(element, deltaState.children);
    }

    updateChildLayouts(): void {
        let zIndex = 0;
        for (let childId of this.state.children) {
            let child = getInstanceByComponentId(childId);

            child.replaceLayoutCssProperties({ zIndex: `${zIndex}` });
            zIndex += 1;
        }
    }
}
