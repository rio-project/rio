import { ComponentId } from '../models';
import { ComponentState } from './componentBase';
import { SingleContainer } from './singleContainer';

export type StackState = ComponentState & {
    _type_: 'Stack-builtin';
    children?: ComponentId[];
};

export class StackComponent extends SingleContainer {
    state: Required<StackState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-stack');
        return element;
    }

    updateElement(deltaState: StackState): void {
        this.replaceChildren(deltaState.children);
    }
}
