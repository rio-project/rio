import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';
import { ComponentId } from '../models';

export type PlaceholderState = ComponentState & {
    _type_: 'Placeholder'; // Not 'Placeholder-builtin'!
    _child_?: ComponentId;
};

export class PlaceholderComponent extends SingleContainer {
    state: Required<PlaceholderState>;

    createElement(): HTMLElement {
        return document.createElement('div');
    }

    updateElement(deltaState: PlaceholderState): void {
        this.replaceOnlyChild(deltaState._child_);
    }
}
