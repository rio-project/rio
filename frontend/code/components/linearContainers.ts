import { pixelsPerEm } from '../app';
import { replaceChildren } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentBase, ComponentState } from './componentBase';

export type LinearContainerState = ComponentState & {
    _type_: 'row' | 'column';
    children?: (number | string)[];
    spacing?: number;
};
// TODO

class LinearContainer extends ComponentBase {
    state: Required<LinearContainerState>;

    protected undef1: HTMLElement;
    protected undef2: HTMLElement;

    protected nGrowers: number; // Number of children that grow in the major axis

    createElement(): HTMLElement {
        let element = document.createElement('div');

        this.undef1 = document.createElement('div');
        this.undef1.classList.add('rio-undefined-space');

        this.undef2 = document.createElement('div');
        this.undef2.classList.add('rio-undefined-space');

        return element;
    }

    updateElement(
        element: HTMLElement,
        deltaState: LinearContainerState
    ): void {
        // Children
        this.undef1.remove();
        this.undef2.remove();
        replaceChildren(element.id, element, deltaState.children);

        // Spacing
        if (deltaState.spacing !== undefined) {
            element.style.gap = `${deltaState.spacing}rem`;
        }

        // Re-layout
        this.makeLayoutDirty();
    }
}

export class RowComponent extends LinearContainer {
    createElement(): HTMLElement {
        let element = super.createElement();
        element.classList.add('rio-row');
        return element;
    }

    updateRequestedWidth(ctx: LayoutContext): void {
        this.requestedWidth = 0;
        this.nGrowers = 0;
        let children = ctx.directChildren(this);

        // Add up all children's requested widths
        for (let child of children) {
            this.requestedWidth += child.requestedWidth;
            // @ts-ignore
            this.nGrowers += child.state['_grow_'][0] as number;
        }

        // Account for spacing
        this.requestedWidth +=
            Math.max(children.length - 1, 0) * this.state.spacing;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        let additionalSpace = this.allocatedWidth - this.requestedWidth;
        let spacePerGrower = additionalSpace / this.nGrowers;

        for (let child of ctx.directChildren(this)) {
            child.allocatedWidth = child.requestedWidth;

            if (child.state['_grow_'][0]) {
                child.allocatedWidth += spacePerGrower;
            }
        }
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        this.requestedHeight = 0;

        for (let child of ctx.directChildren(this)) {
            this.requestedHeight = Math.max(
                this.requestedHeight,
                child.requestedHeight
            );
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Is all allocated space used? Highlight any undefined space
        let additionalSpace = this.allocatedWidth - this.requestedWidth;

        if (this.nGrowers > 0 || Math.abs(additionalSpace) < 1e-6) {
        } else {
            // If there is no child elements make a single undefined space take
            // up everything. This way there is no unsightly disconnect between
            // the two.
            let element = this.element();

            if (element.children.length === 0) {
                element.appendChild(this.undef1);
            } else {
                element.insertBefore(this.undef1, element.children[0]);
                element.appendChild(this.undef2);
            }

            console.log(
                `Warning: Component #${this.elementId} has ${
                    additionalSpace * pixelsPerEm
                }px of unused space`
            );
        }

        // Position the children
        for (let child of ctx.directChildren(this)) {
            // Assign the allocated height to the children
            child.allocatedHeight = this.allocatedHeight;

            // Move it around
            let element = child.element();
            element.style.left = '0';
            element.style.top = '0';

            // Grow?
            // element.style.flexGrow = child.state['_grow_'][0] ? '1' : '0';
        }
    }
}

export class ColumnComponent extends RowComponent {}
