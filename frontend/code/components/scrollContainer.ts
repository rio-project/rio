import { componentsById } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { SCROLL_BAR_SIZE } from '../utils';
import { ComponentBase, ComponentState } from './componentBase';
// TODO

export type ScrollContainerState = ComponentState & {
    _type_: 'ScrollContainer-builtin';
    child?: ComponentId;
    scroll_x?: 'never' | 'auto' | 'always';
    scroll_y?: 'never' | 'auto' | 'always';
};

const SCROLL_TO_OVERFLOW = {
    never: 'hidden',
    auto: 'auto',
    always: 'scroll',
};

const NATURAL_SIZE = 1.0;

export class ScrollContainerComponent extends ComponentBase {
    state: Required<ScrollContainerState>;

    private assumeVerticalScrollBarWillBeNeeded: boolean = true;
    private incorrectAssumptionCount: number = 0;

    private get layoutWithVerticalScrollbar(): boolean {
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

        if (deltaState.scroll_x !== undefined) {
            this.element.style.overflowX =
                SCROLL_TO_OVERFLOW[deltaState.scroll_x];
        }

        if (deltaState.scroll_y !== undefined) {
            this.element.style.overflowY =
                SCROLL_TO_OVERFLOW[deltaState.scroll_y];
        }

        this.makeLayoutDirty();
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth = NATURAL_SIZE;

        // If there will be a vertical scroll bar, reserve space for it
        if (this.layoutWithVerticalScrollbar) {
            this.naturalWidth += SCROLL_BAR_SIZE;
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        let child = componentsById[this.state.child]!;

        // If the child needs more space than we have, we'll need to display a
        // scroll bar. So just give the child the width it wants.
        if (child.requestedWidth > this.allocatedWidth) {
            child.allocatedWidth = child.requestedWidth;
            return;
        }

        // Otherwise, stretch the child to use up all the available width
        if (this.layoutWithVerticalScrollbar) {
            child.allocatedWidth = this.allocatedWidth - SCROLL_BAR_SIZE;
        } else {
            child.allocatedWidth = this.allocatedWidth;
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        this.naturalHeight = NATURAL_SIZE;

        // If there will be a horizontal scroll bar, reserve space for it
        if (
            this.state.scroll_x === 'always' ||
            componentsById[this.state.child]!.allocatedWidth >
                this.allocatedWidth
        ) {
            this.naturalHeight += SCROLL_BAR_SIZE;
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        let child = componentsById[this.state.child]!;

        // First, check if our assumption for the vertical scroll bar was
        // correct. If not, we have to immediately re-layout the child.
        if (this.state.scroll_y === 'auto') {
            let assumptionWasCorrect = this.assumeVerticalScrollBarWillBeNeeded
                ? this.allocatedHeight < child.requestedHeight
                : this.allocatedHeight >= child.requestedHeight;

            if (!assumptionWasCorrect) {
                // Theoretically, there could be a situation where our
                // assumptions are always wrong and we re-layout endlessly.
                //
                // It's acceptable to have an unnecessary scroll bar, but it's
                // not acceptable to be missing a scroll bar when one is
                // required. So we will only re-layout if this is the first time
                // our assumption was wrong, or if we don't currently have a
                // scroll bar.
                if (
                    this.incorrectAssumptionCount == 0 ||
                    !this.assumeVerticalScrollBarWillBeNeeded
                ) {
                    this.incorrectAssumptionCount++;
                    this.assumeVerticalScrollBarWillBeNeeded =
                        !this.assumeVerticalScrollBarWillBeNeeded;

                    ctx.requestImmediateReLayout(() => {
                        this.makeLayoutDirty();
                    });
                    return;
                }
            }
        }

        this.incorrectAssumptionCount = 0;

        // If the child needs more space than we have, we'll need to display a
        // scroll bar. So just give the child the height it wants.
        if (child.requestedHeight > this.allocatedHeight) {
            child.allocatedHeight = child.requestedHeight;
            return;
        }

        // Otherwise, stretch the child to use up all the available height
        if (this.state.scroll_x === 'always') {
            child.allocatedHeight = this.allocatedHeight - SCROLL_BAR_SIZE;
        } else {
            child.allocatedHeight = this.allocatedHeight;
        }
    }
}
