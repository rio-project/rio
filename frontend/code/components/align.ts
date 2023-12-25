import {
    getInstanceByComponentId,
    replaceOnlyChild,
} from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentBase, ComponentState } from './componentBase';

export type AlignState = ComponentState & {
    _type_: 'Align-builtin';
    child?: number | string;
    align_x?: number | null;
    align_y?: number | null;
};

export class AlignComponent extends ComponentBase {
    state: Required<AlignState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: AlignState): void {
        replaceOnlyChild(element.id, element, deltaState.child);

        this.makeLayoutDirty();
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth = ctx.inst(this.state.child).requestedWidth;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        let childInstance = ctx.inst(this.state.child);
        let childElement = ctx.elem(this.state.child);

        if (this.state.align_x === null) {
            childInstance.allocatedWidth = this.allocatedWidth;
            childElement.style.left = '0';
        } else {
            childInstance.allocatedWidth = childInstance.requestedWidth;

            let additionalSpace =
                this.allocatedWidth - childInstance.requestedWidth;
            childElement.style.left =
                additionalSpace * this.state.align_x + 'rem';
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        this.naturalHeight = ctx.inst(this.state.child).requestedHeight;
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        let childInstance = ctx.inst(this.state.child);
        let childElement = ctx.elem(this.state.child);

        if (this.state.align_y === null) {
            childInstance.allocatedHeight = this.allocatedHeight;
            childElement.style.top = '0';
        } else {
            childInstance.allocatedHeight = childInstance.requestedHeight;

            let additionalSpace =
                this.allocatedHeight - childInstance.requestedHeight;
            childElement.style.top =
                additionalSpace * this.state.align_y + 'rem';
        }
    }
}
