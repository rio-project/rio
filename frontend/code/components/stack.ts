import { getInstanceByComponentId, replaceChildrenAndResetCssProperties } from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type StackState = ComponentState & {
    _type_: 'stack';
    children?: number[];
};

export class StackComponent extends ComponentBase {
    state: Required<StackState>;

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-stack');
        return element;
    }

    _updateElement(element: HTMLElement, deltaState: StackState): void {
        replaceChildrenAndResetCssProperties(element, deltaState.children);
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
