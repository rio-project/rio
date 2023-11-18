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
        // Update the children. They are wrapped in divs, to allow CSS to spawn
        // separators between them. Those separators would be the wrong size if
        // the children were not wrapped in divs.
        replaceChildrenAndResetCssProperties(
            element,
            deltaState.children,
            true
        );

        // Make sure the added divs are single containers
        for (let child of element.children) {
            child.classList.add('rio-single-container');
        }
    }
}
