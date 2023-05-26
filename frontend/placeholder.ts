import { replaceOnlyChild } from './app';
import { WidgetState } from './widgetBase';


export type PlaceholderState = WidgetState & {
    _type_: 'placeholder';
    _child_?: number;
};

export class PlaceholderWidget {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: PlaceholderState): void {
        replaceOnlyChild(element, deltaState._child_);
    }
}
