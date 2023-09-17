
import { replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type ScrollTargetState = WidgetState & {
    _type_: 'ScrollTarget-builtin';
    id?: string;
    child?: number | string | null;
};


export class ScrollTargetWidget extends WidgetBase {
    state: Required<ScrollTargetState>;

    createElement(): HTMLElement {
        // We need to set the element's id, but elements for widgets must all
        // have ids of the form `reflex-id-...`. So we must create a container
        // for our <a> element.
        let element = document.createElement('span');

        let anchorElement = document.createElement('a');
        element.appendChild(anchorElement);

        return element;
    }

    updateElement(element: HTMLElement, deltaState: ScrollTargetState): void {
        let anchorElement = element.firstElementChild as HTMLElement;

        replaceOnlyChild(anchorElement, deltaState.child);

        if (deltaState.id !== undefined) {
            anchorElement.id = deltaState.id;
        }
    }
}

