import {
    getInstanceByComponentId,
    replaceOnlyChild,
} from '../componentManagement';
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

    updateRequestedWidth(): void {
        this.requestedWidth = getInstanceByComponentId(
            this.state.child
        ).requestedWidth;
    }

    updateAllocatedWidth(): void {
        let childInstance = getInstanceByComponentId(this.state.child);
        let childElement = childInstance.element();

        if (this.state.align_x === null) {
            childInstance.allocatedWidth = this.allocatedWidth;
            childElement.style.left = '0';
        } else {
            childInstance.allocatedWidth = childInstance.requestedWidth;
            childElement.style.left =
                (this.allocatedWidth - childInstance.requestedWidth) *
                    this.state.align_x +
                'px';
        }
    }

    updateRequestedHeight(): void {
        this.requestedHeight = getInstanceByComponentId(
            this.state.child
        ).requestedHeight;
    }

    updateAllocatedHeight(): void {
        let childInstance = getInstanceByComponentId(this.state.child);
        let childElement = childInstance.element();

        if (this.state.align_y === null) {
            childInstance.allocatedHeight = this.allocatedHeight;
            childElement.style.top = '0';
        } else {
            childInstance.allocatedHeight = childInstance.requestedHeight;
            childElement.style.top =
                (this.allocatedHeight - childInstance.requestedHeight) *
                    this.state.align_y +
                'px';
        }
    }
}
