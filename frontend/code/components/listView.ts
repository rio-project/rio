import {
    getInstanceByComponentId,
    replaceChildrenAndResetCssProperties,
} from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type ListViewState = ComponentState & {
    children?: (number | string)[];
};

export class ListViewComponent extends ComponentBase {
    state: Required<ListViewState>;

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-list-view');
        return element;
    }

    _updateElement(element: HTMLElement, deltaState: ListViewState): void {
        replaceChildrenAndResetCssProperties(element, deltaState.children);
    }
}
