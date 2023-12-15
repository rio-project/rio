import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';
import { replaceOnlyChild } from '../componentManagement';

export type PlaceholderState = ComponentState & {
    _type_: 'Placeholder';
    _child_?: number | string;
};

export class PlaceholderComponent extends SingleContainer {
    state: Required<PlaceholderState>;

    createElement(): HTMLElement {
        return document.createElement('div');
    }

    updateElement(element: HTMLElement, deltaState: PlaceholderState): void {
        replaceOnlyChild(element.id, element, deltaState._child_);
        this.makeLayoutDirty();
    }
}
