import { ComponentBase, ComponentState } from './componentBase';
import { replaceOnlyChild } from '../componentManagement';
import { LayoutContext } from '../layouting';

export type MarginState = ComponentState & {
    _type_: 'Margin-builtin';
    child?: number | string;
    margin_left?: number;
    margin_top?: number;
    margin_right?: number;
    margin_bottom?: number;
};

export class MarginComponent extends ComponentBase {
    state: Required<MarginState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: MarginState): void {
        replaceOnlyChild(element.id, element, deltaState.child);

        this.makeLayoutDirty();
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth =
            ctx.inst(this.state.child).requestedWidth +
            this.state.margin_left +
            this.state.margin_right;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        let childInstance = ctx.inst(this.state.child);
        childInstance.allocatedWidth =
            this.allocatedWidth -
            this.state.margin_left -
            this.state.margin_right;
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        this.naturalHeight =
            ctx.inst(this.state.child).requestedHeight +
            this.state.margin_top +
            this.state.margin_bottom;
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        let childInstance = ctx.inst(this.state.child);
        childInstance.allocatedHeight =
            this.allocatedHeight -
            this.state.margin_top -
            this.state.margin_bottom;

        let childElement = ctx.elem(this.state.child);
        childElement.style.left = `${this.state.margin_left}rem`;
        childElement.style.top = `${this.state.margin_top}rem`;
    }
}
