import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';

export type PlaceholderState = ComponentState & {
    _type_: 'Placeholder';
    _child_?: number | string;
};

export class PlaceholderComponent extends SingleContainer {
    state: Required<PlaceholderState>;

    _createElement(): HTMLElement {
        return document.createElement('div');
    }
}
