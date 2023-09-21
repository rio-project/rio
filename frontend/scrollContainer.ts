import { getInstanceByWidgetId, replaceOnlyChild } from './app';
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

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-scroll-container', 'rio-single-container');
        return element;
    }

    updateElement(
        element: HTMLElement,
        deltaState: ScrollContainerState
    ): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.scroll_x !== undefined) {
            element.style.overflowX = SCROLL_TO_OVERFLOW[deltaState.scroll_x];
        }

        if (deltaState.scroll_y !== undefined) {
            element.style.overflowY = SCROLL_TO_OVERFLOW[deltaState.scroll_y];
        }
    }

    updateChildLayouts(): void {
        let child = this.state['child'];

        if (child !== undefined && child !== null) {
            getInstanceByWidgetId(child).replaceLayoutCssProperties({});
        }
    }
}
