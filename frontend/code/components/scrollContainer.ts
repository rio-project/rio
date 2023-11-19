import {
    getInstanceByComponentId,
    replaceOnlyChildAndResetCssProperties,
} from '../componentManagement';
import { SCROLL_BAR_SIZE } from '../utils';
import { ComponentBase, ComponentState } from './componentBase';

export type ScrollContainerState = ComponentState & {
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

export class ScrollContainerComponent extends ComponentBase {
    state: Required<ScrollContainerState>;

    private _innerElement: HTMLElement;
    private _resizeObserver: ResizeObserver | null = null;

    // Consists of two elements:
    // 1. A container element that simply has `position: relative` so that its
    //    child can copy its size with `100%`.
    // 2. The element that actually scrolls. This has `position: absolute` so
    //    that no matter how large its contents are, the parent element will
    //    always have a minimum size of 0x0.
    //
    // And finally, there's the child component of the ScrollContainer, which must
    // never be smaller than the ScrollContainer itself. This is achieved by
    // giving it a `min-width` and `min-height` of 100%.
    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add(
            'rio-scroll-container',
            'rio-zero-size-request-container'
        );

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
    private _onChildSizeChange(
        entries: ResizeObserverEntry[],
        observer: ResizeObserver
    ): void {
        let element = this.tryGetElement();

        // If the parent isn't alive anymore, remove the observer
        if (element === null) {
            observer.disconnect();
            return;
        }

        for (let entry of entries) {
            let child = entry.target as HTMLElement;
            this._resizeToFitChild(child);
        }
    }

    private _resizeToFitChild(child: HTMLElement): void {
        let minWidth: string | null = null;
        let minHeight: string | null = null;

        let element = this.element();

        if (this.state.scroll_x === 'never') {
            let hasVerticalScrollbar =
                this.state.scroll_y === 'always' ||
                (this.state.scroll_y === 'auto' &&
                    child.scrollHeight > element.clientHeight);

            if (hasVerticalScrollbar) {
                minWidth = `${child.scrollWidth + SCROLL_BAR_SIZE}px`;
            } else {
                minWidth = `${child.scrollWidth}px`;
            }
        }

        if (this.state.scroll_y === 'never') {
            let hasHorizontalScrollbar =
                this.state.scroll_x === 'always' ||
                (this.state.scroll_x === 'auto' &&
                    child.scrollWidth > element.clientWidth);

            if (hasHorizontalScrollbar) {
                minHeight = `${child.scrollHeight + SCROLL_BAR_SIZE}px`;
            } else {
                minHeight = `${child.scrollHeight}px`;
            }
        }

        this.setMinSizeComponentImpl(minWidth, minHeight);
    }

    _updateElement(
        element: HTMLElement,
        deltaState: ScrollContainerState
    ): void {
        if (deltaState.child !== undefined) {
            // New child? Remove the old ResizeObserver and the assigned
            // width/height.
            if (this._resizeObserver !== null) {
                this._resizeObserver.disconnect();
                this._resizeObserver = null;

                this.setMinSizeComponentImpl(null, null);
            }

            replaceOnlyChildAndResetCssProperties(
                element.id,
                this._innerElement,
                deltaState.child
            );

            let child = getInstanceByComponentId(deltaState.child);
            child.replaceLayoutCssProperties({});

            this._resizeToFitChild(child.element());
        }

        if (deltaState.scroll_x !== undefined) {
            this._innerElement.style.overflowX =
                SCROLL_TO_OVERFLOW[deltaState.scroll_x];
        }

        if (deltaState.scroll_y !== undefined) {
            this._innerElement.style.overflowY =
                SCROLL_TO_OVERFLOW[deltaState.scroll_y];
        }

        // Check if we need to attach a ResizeObserver to the child
        if (this._resizeObserver === null) {
            let scrollX = deltaState.scroll_x || this.state.scroll_x;
            let scrollY = deltaState.scroll_y || this.state.scroll_y;

            if (scrollX === 'never' || scrollY === 'never') {
                this._resizeObserver = new ResizeObserver(
                    this._onChildSizeChange.bind(this)
                );
                this._resizeObserver.observe(
                    this._innerElement.firstElementChild!
                );
            }
        }
    }
}
