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
        if (this.state.scroll_y === 'always') {
            this.naturalWidth += SCROLL_BAR_SIZE;
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        let child = componentsById[this.state.child]!;

        // If the child needs more space than we have, we'll need to display a
        // scroll bar. So just give the child the width it wants.
        if (child.naturalWidth > this.allocatedWidth) {
            child.allocatedWidth = child.naturalWidth;
            return;
        }

        // Otherwise, stretch the child to use up all the available width
        if (this.state.scroll_y === 'always') {
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

        // If the child needs more space than we have, we'll need to display a
        // scroll bar. So just give the child the height it wants.
        if (child.naturalHeight > this.allocatedHeight) {
            child.allocatedHeight = child.naturalHeight;
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
