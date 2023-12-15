import { replaceChildren } from '../componentManagement';
import { ComponentState } from './componentBase';
import { SingleContainer } from './singleContainer';

// TODO: set child z-indices, if necessary!?

export type StackState = ComponentState & {
    _type_: 'stack';
    children?: number[];
};

export class StackComponent extends SingleContainer {
    state: Required<StackState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-stack');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: StackState): void {
        replaceChildren(element.id, element, deltaState.children);
        this.makeLayoutDirty();
    }
}
