import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';
import { replaceOnlyChild } from '../componentManagement';

export type PlaceholderState = ComponentState & {
    _type_: 'Placeholder'; // Not 'Placeholder-builtin'!
    _child_?: number | string;
};

export class PlaceholderComponent extends SingleContainer {
    state: Required<PlaceholderState>;

    createElement(): HTMLElement {
        return document.createElement('div');
    }

    updateElement(deltaState: PlaceholderState): void {
        replaceOnlyChild(this.element.id, this.element, deltaState._child_);
        this.makeLayoutDirty();
    }
}
