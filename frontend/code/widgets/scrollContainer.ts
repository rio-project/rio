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
    private _resizeObserver: ResizeObserver | null = null;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-scroll-container', 'rio-zero-size-request-container');

        this._innerElement = document.createElement('div');
        element.appendChild(this._innerElement);

        return element;
    }

    // In order to make nested ScrollContainers work, we have made the
    // ScrollContainer's child `absolute` positioned. This essentially makes it
    // use up as little space as possible. The problem is that this isn't what
    // we want when scrolling is set to `never`.
    //
    // As a half-solution, if scrolling is set to `never`, we attach a
    // ResizeObserver to the child that copies its dimensions to the
    // ScrollContainer's inner element. This ensures that the child will never
    // be too large for the ScrollContainer. But since children fill up their
    // entire parent, the child's size can only ever grow and never shrink.
    _onChildSizeChange(entries: ResizeObserverEntry[], observer: ResizeObserver): void {
        let element = this.tryGetElement();

        // If the parent isn't alive anymore, remove the observer
        if (element === null) {
            observer.disconnect();
            return;
        }

        for (let entry of entries) {
            let child = entry.target as HTMLElement;
            let width = child.scrollWidth;
            let height = child.scrollHeight;

            if (this.state.scroll_x === 'never') {
                element.style.minWidth = `${width}px`;
            }

            if (this.state.scroll_y === 'never') {
                element.style.minHeight = `${height}px`;
            }
        }
    }

    updateElement(
        element: HTMLElement,
        deltaState: ScrollContainerState
    ): void {
        if (deltaState.child !== undefined) {
            // New child? Remove the old ResizeObserver and the assigned
            // width/height.
            if (this._resizeObserver !== null) {
                this._resizeObserver.disconnect();
                this._resizeObserver = null;

                element.style.minWidth = '';
                element.style.minHeight = '';
            }

            replaceOnlyChild(this._innerElement, deltaState.child);
        }

        if (deltaState.scroll_x !== undefined) {
            this._innerElement.style.overflowX = SCROLL_TO_OVERFLOW[deltaState.scroll_x];
        }

        if (deltaState.scroll_y !== undefined) {
            this._innerElement.style.overflowY = SCROLL_TO_OVERFLOW[deltaState.scroll_y];
        }

        // Check if we need to attach a ResizeObserver to the child
        if (this._resizeObserver === null) {
            let scrollX = deltaState.scroll_x || this.state.scroll_x;
            let scrollY = deltaState.scroll_y || this.state.scroll_y;

            if (scrollX === 'never' || scrollY === 'never') {
                this._resizeObserver = new ResizeObserver(this._onChildSizeChange.bind(this));
                this._resizeObserver.observe(this._innerElement.firstElementChild!);
            }
        }
    }

    updateChildLayouts(): void {
        let child = this.state['child'];

        if (child !== undefined && child !== null) {
            getInstanceByWidgetId(child).replaceLayoutCssProperties({});
        }
    }
}
