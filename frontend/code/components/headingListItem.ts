import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';
import { textStyleToCss } from '../cssUtils';

export type HeadingListItemState = ComponentState & {
    _type_: 'CustomListItem-builtin';
    text?: string;
};

export class HeadingListItemComponent extends SingleContainer {
    state: Required<HeadingListItemState>;

    _createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-heading-list-item');

        // Apply a style. This could be done with CSS, instead of doing it
        // individually for each component, but these are rare and this preempts
        // duplicate code.
        Object.assign(element.style, textStyleToCss('heading3'));

        return element;
    }

    _updateElement(
        element: HTMLElement,
        deltaState: HeadingListItemState
    ): void {
        if (deltaState.text !== undefined) {
            element.textContent = deltaState.text;
        }
    }
}
