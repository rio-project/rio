import {
    getInstanceByComponentId,
    replaceOnlyChild,
} from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type PlaceholderState = ComponentState & {
    _type_: 'Placeholder';
    _child_?: number | string;
};

export class PlaceholderComponent extends ComponentBase {
    state: Required<PlaceholderState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-single-container');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: PlaceholderState): void {
        replaceOnlyChild(element, deltaState._child_);
    }

    updateChildLayouts(): void {
        getInstanceByComponentId(
            this.state['_child_']
        ).replaceLayoutCssProperties({});
    }
}
