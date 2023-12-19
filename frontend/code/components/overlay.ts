import { getRootInstance, replaceOnlyChild } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';

export type OverlayState = ComponentState & {
    _type_: 'Overlay-builtin';
    child?: ComponentId;
};

export class OverlayComponent extends ComponentBase {
    state: Required<OverlayState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-overlay');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: OverlayState): void {
        replaceOnlyChild(element.id, element, deltaState.child);
        this.makeLayoutDirty();
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        // The root component keeps track of the correct overlay size. Take it
        // from there. To heck with what the parent says.
        let root = getRootInstance();
        ctx.inst(this.state.child).allocatedWidth = root.overlayWidth;
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Honor the global overlay height.
        let root = getRootInstance();
        ctx.inst(this.state.child).allocatedHeight = root.overlayHeight;

        // Position the child
        let element = ctx.elem(this.state.child);
        element.style.left = '0';
        element.style.top = '0';
    }
}
