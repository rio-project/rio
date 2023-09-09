import { replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type StickyState = WidgetState & {
    _type_: 'Sticky-builtin';
    child?: number | string;
};

export class StickyWidget extends WidgetBase {
    state: Required<StickyState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-sticky');
        element.classList.add('reflex-single-container');

        return element;
    }

    updateElement(element: HTMLElement, deltaState: StickyState): void {
        replaceOnlyChild(element, deltaState.child);
    }
}
