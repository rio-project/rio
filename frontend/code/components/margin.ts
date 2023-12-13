import { SingleContainer } from './singleContainer';
import { ComponentBase, ComponentState } from './componentBase';
import {
    getInstanceByComponentId,
    replaceOnlyChild,
} from '../componentManagement';
import { pixelsPerEm } from '../app';

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

    updateRequestedWidth(): void {
        this.requestedWidth =
            getInstanceByComponentId(this.state.child).requestedWidth +
            pixelsPerEm * this.state.margin_left +
            pixelsPerEm * this.state.margin_right;
    }

    updateAllocatedWidth(): void {
        let childInstance = getInstanceByComponentId(this.state.child);
        childInstance.allocatedWidth =
            this.allocatedWidth -
            pixelsPerEm * this.state.margin_left -
            pixelsPerEm * this.state.margin_right;
    }

    updateRequestedHeight(): void {
        this.requestedHeight =
            getInstanceByComponentId(this.state.child).requestedHeight +
            pixelsPerEm * this.state.margin_top +
            pixelsPerEm * this.state.margin_bottom;
    }

    updateAllocatedHeight(): void {
        let childInstance = getInstanceByComponentId(this.state.child);
        childInstance.allocatedHeight =
            this.allocatedHeight -
            pixelsPerEm * this.state.margin_top -
            pixelsPerEm * this.state.margin_bottom;

        let childElement = childInstance.element();
        childElement.style.left = `${this.state.margin_left}rem`;
        childElement.style.top = `${this.state.margin_top}rem`;
    }
}
