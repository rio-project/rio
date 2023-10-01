import { getInstanceByWidgetId, replaceOnlyChild } from '../widgetManagement';
import { WidgetBase, WidgetState } from './widgetBase';

export type ScrollContainerState = WidgetState & {
    _type_: 'ScrollContainer-builtin';
    child?: number | string;
    scroll_x?: 'never' | 'auto' | 'always';
    scroll_y?: 'never' | 'auto' | 'always';
};

const SCROLL_TO_OVERFLOW = {
    never: 'hidden',
    auto: 'auto',
    always: 'scroll',
};

export class ScrollContainerWidget extends WidgetBase {
    state: Required<ScrollContainerState>;

    private _innerElement: HTMLElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-scroll-container', 'rio-zero-size-request-container');

        this._innerElement = document.createElement('div');
        element.appendChild(this._innerElement);

        return element;
    }

    updateElement(
        element: HTMLElement,
        deltaState: ScrollContainerState
    ): void {
        replaceOnlyChild(this._innerElement, deltaState.child);

        if (deltaState.scroll_x !== undefined) {
            this._innerElement.style.overflowX = SCROLL_TO_OVERFLOW[deltaState.scroll_x];
        }

        if (deltaState.scroll_y !== undefined) {
            this._innerElement.style.overflowY = SCROLL_TO_OVERFLOW[deltaState.scroll_y];
        }
    }

    updateChildLayouts(): void {
        let child = this.state['child'];

        if (child !== undefined && child !== null) {
            getInstanceByWidgetId(child).replaceLayoutCssProperties({});
        }
    }
}
