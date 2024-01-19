import { pixelsPerEm, scrollBarSize } from '../app';
import { componentsById } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';

export type ScrollContainerState = ComponentState & {
    _type_: 'ScrollContainer-builtin';
    child?: ComponentId;
    scroll_x?: 'never' | 'auto' | 'always';
    scroll_y?: 'never' | 'auto' | 'always';
    sticky_bottom?: boolean;
};

const NATURAL_SIZE = 1.0;

export class ScrollContainerComponent extends ComponentBase {
    state: Required<ScrollContainerState>;

    private assumeVerticalScrollBarWillBeNeeded: boolean = true;
    private numSequentialIncorrectAssumptions: number = 0;

    private shouldLayoutWithVerticalScrollbar(): boolean {
        switch (this.state.scroll_y) {
            case 'always':
                return true;

            case 'auto':
                return this.assumeVerticalScrollBarWillBeNeeded;

            case 'never':
                return false;
        }
    }

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-scroll-container');
        return element;
    }

    updateElement(
        deltaState: ScrollContainerState,
        latentComponents: Set<ComponentBase>
    ): void {
        this.replaceOnlyChild(latentComponents, deltaState.child);
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        if (this.state.sticky_bottom)
            console.debug('scrollTop NW (px):', this.element.scrollTop);

        if (this.state.scroll_x === 'never') {
            let child = componentsById[this.state.child]!;
            this.naturalWidth = child.requestedWidth;
            return;
        }

        this.naturalWidth = NATURAL_SIZE;

        // If there will be a vertical scroll bar, reserve space for it
        if (this.shouldLayoutWithVerticalScrollbar()) {
            this.naturalWidth += scrollBarSize;
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        if (this.state.sticky_bottom)
            console.debug('scrollTop AW (px):', this.element.scrollTop);
        let child = componentsById[this.state.child]!;

        let availableWidth = this.allocatedWidth;
        if (this.shouldLayoutWithVerticalScrollbar()) {
            availableWidth -= scrollBarSize;
        }

        // If the child needs more space than we have, we'll need to display a
        // scroll bar. So just give the child the width it wants.
        if (child.requestedWidth > availableWidth) {
            child.allocatedWidth = child.requestedWidth;
            this.element.style.overflowX = 'scroll';
        } else {
            // Otherwise, stretch the child to use up all the available width
            child.allocatedWidth = availableWidth;

            this.element.style.overflowX =
                this.state.scroll_x === 'always' ? 'scroll' : 'hidden';
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        if (this.state.sticky_bottom)
            console.debug('scrollTop NH (px):', this.element.scrollTop);
        if (this.state.scroll_y === 'never') {
            let child = componentsById[this.state.child]!;
            this.naturalHeight = child.requestedHeight;
            return;
        }

        this.naturalHeight = NATURAL_SIZE;

        // If there will be a horizontal scroll bar, reserve space for it
        if (this.element.style.overflowX === 'scroll') {
            this.naturalHeight += scrollBarSize;
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        if (this.state.sticky_bottom)
            console.debug('scrollTop AH (px):', this.element.scrollTop);
        let child = componentsById[this.state.child]!;

        let heightBefore = child.allocatedHeight;

        let availableHeight = this.allocatedHeight;
        if (this.element.style.overflowX === 'scroll') {
            availableHeight -= scrollBarSize;
        }

        // If the child needs more space than we have, we'll need to display a
        // scroll bar. So just give the child the height it wants.
        let newAllocatedHeight: number;
        if (child.requestedHeight > availableHeight) {
            newAllocatedHeight = child.requestedHeight;
            this.element.style.overflowY = 'scroll';
        } else {
            // Otherwise, stretch the child to use up all the available height
            newAllocatedHeight = availableHeight;

            if (this.state.scroll_y === 'always') {
                this.element.style.overflowY = 'scroll';
            } else {
                this.element.style.overflowY = 'hidden';
            }
        }

        // Now check if our assumption for the vertical scroll bar was correct.
        // If not, we have to immediately re-layout the child.
        let hasVerticalScrollbar = this.element.style.overflowY === 'scroll';
        if (
            this.state.scroll_y === 'auto' &&
            this.assumeVerticalScrollBarWillBeNeeded !== hasVerticalScrollbar
        ) {
            // Theoretically, there could be a situation where our assumptions
            // are always wrong and we re-layout endlessly.
            //
            // It's acceptable to have an unnecessary scroll bar, but it's not
            // acceptable to be missing a scroll bar when one is required. So we
            // will only re-layout if this is the first time our assumption was
            // wrong, or if we don't currently have a scroll bar.
            if (
                this.numSequentialIncorrectAssumptions == 0 ||
                !this.assumeVerticalScrollBarWillBeNeeded
            ) {
                this.numSequentialIncorrectAssumptions++;
                this.assumeVerticalScrollBarWillBeNeeded =
                    !this.assumeVerticalScrollBarWillBeNeeded;

                ctx.requestImmediateReLayout(() => {
                    this.makeLayoutDirty();
                });
                return;
            }
        }

        this.numSequentialIncorrectAssumptions = 0;

        // Only change the allocatedHeight once we're sure that we won't be
        // re-layouting again
        child.allocatedHeight = newAllocatedHeight;

        // If `sticky_bottom` is enabled, check if we have to scroll down
        console.debug('Child allocated height before:', heightBefore);
        console.debug('Child allocated height after:', child.allocatedHeight);
        if (this.state.sticky_bottom && child.allocatedHeight > heightBefore) {
            // Calculate how much of the child is visible
            let visibleHeight = this.allocatedHeight;
            if (this.element.style.overflowX === 'scroll') {
                visibleHeight -= scrollBarSize;
            }
            console.debug('visible height:', visibleHeight);
            console.debug('scrollTop (px):', this.element.scrollTop);
            console.debug(
                'bounding height (px):',
                child.element.getBoundingClientRect().height
            );
            console.debug(
                'child.element.style.height:',
                child.element.style.height
            );

            // Check if the scrollbar is all the way at the bottom
            if (
                (this.element.scrollTop + 1) / pixelsPerEm + visibleHeight >=
                heightBefore - 0.00001
            ) {
                console.debug('Scrolling to', child.allocatedHeight);
                // Our CSS `height` hasn't been updated yet, so we can't scroll
                // down any further. We must assign the `height` manually.
                this.element.style.height = `${
                    this.allocatedHeight * pixelsPerEm
                }px`;
                child.element.style.height = `${
                    child.allocatedHeight * pixelsPerEm
                }px`;

                this.element.scroll({
                    top: child.allocatedHeight * pixelsPerEm + 1000,
                    left: this.element.scrollLeft,
                    behavior: 'instant',
                });
            }
        }
    }
}
