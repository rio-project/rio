import { replaceOnlyChildAndResetCssProperties } from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type ScrollTargetState = ComponentState & {
    _type_: 'ScrollTarget-builtin';
    id?: string;
    child?: number | string | null;
};

export class ScrollTargetComponent extends ComponentBase {
    state: Required<ScrollTargetState>;

    constructor(elementId: string, state: ComponentState) {
        super(elementId, state);

        this._minSizeComponentImpl[0] = 'fit-content';
    }

    _createElement(): HTMLElement {
        // We need to set the element's id, but elements for components must all
        // have ids of the form `rio-id-...`. So we must create a container
        // for our <a> element.
        let element = document.createElement('span');
        element.classList.add('rio-single-container');

        let anchorElement = document.createElement('a');
        anchorElement.classList.add('rio-single-container');
        element.appendChild(anchorElement);

        return element;
    }

    _updateElement(element: HTMLElement, deltaState: ScrollTargetState): void {
        let anchorElement = element.firstElementChild as HTMLElement;

        replaceOnlyChildAndResetCssProperties(anchorElement, deltaState.child);

        if (deltaState.id !== undefined) {
            anchorElement.id = deltaState.id;
        }
    }
}
