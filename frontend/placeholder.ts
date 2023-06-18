import { getInstanceByWidgetId, replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type PlaceholderState = WidgetState & {
    _type_: 'Placeholder';
    _child_?: number | string;
};

export class PlaceholderWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-single-container');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: PlaceholderState): void {
        replaceOnlyChild(element, deltaState._child_);
    }

    updateChildLayouts(): void {
        getInstanceByWidgetId(this.state['_child_']).replaceLayoutCssProperties(
            {}
        );
    }
}
