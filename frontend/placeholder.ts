import { replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type PlaceholderState = WidgetState & {
    _type_: 'placeholder';
    _child_?: number;
};

export class PlaceholderWidget extends WidgetBase {
    createInnerElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-placeholder');
        return element;
    }

    updateInnerElement(
        element: HTMLElement,
        deltaState: PlaceholderState
    ): void {
        replaceOnlyChild(element, deltaState._child_);
    }
}
