import { replaceOnlyChild } from '../componentManagement';
import { ComponentId } from '../models';
import { ComponentState } from './componentBase';
import { SingleContainer } from './singleContainer';

export type ScrollTargetState = ComponentState & {
    _type_: 'ScrollTarget-builtin';
    id?: string;
    child?: ComponentId | null;
};

export class ScrollTargetComponent extends SingleContainer {
    state: Required<ScrollTargetState>;

    createElement(): HTMLElement {
        // We need to set the element's id, but elements for components must all
        // have ids of the form `rio-id-...`. So we must create a container
        // for our <a> element.
        let element = document.createElement('span');

        let anchorElement = document.createElement('a');
        element.appendChild(anchorElement);

        return element;
    }

    updateElement(element: HTMLElement, deltaState: ScrollTargetState): void {
        let anchorElement = element.firstElementChild as HTMLElement;

        replaceOnlyChild(element.id, anchorElement, deltaState.child);

        if (deltaState.id !== undefined) {
            anchorElement.id = deltaState.id;
        }

        this.makeLayoutDirty();
    }
}
