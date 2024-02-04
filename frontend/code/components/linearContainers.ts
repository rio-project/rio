import { pixelsPerRem } from '../app';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';

export type LinearContainerState = ComponentState & {
    _type_: 'Row-builtin' | 'Column-builtin' | 'ListView-builtin';
    children?: ComponentId[];
    spacing?: number;
};

class LinearContainer extends ComponentBase {
    state: Required<LinearContainerState>;

    protected childContainer: HTMLElement;
    protected undef1: HTMLElement;
    protected undef2: HTMLElement;

    protected nGrowers: number; // Number of children that grow in the major axis

    createElement(): HTMLElement {
        let element = document.createElement('div');

        this.undef1 = document.createElement('div');
        this.undef1.classList.add('rio-undefined-space');
        element.appendChild(this.undef1);

        this.childContainer = document.createElement('div');
        this.childContainer.classList.add('rio-linear-child-container');
        element.appendChild(this.childContainer);

        this.undef2 = document.createElement('div');
        this.undef2.classList.add('rio-undefined-space');
        element.appendChild(this.undef2);

        return element;
    }

    updateElement(
        deltaState: LinearContainerState,
        latentComponents: Set<ComponentBase>
    ): void {
        // Children
        if (deltaState.children !== undefined) {
            this.replaceChildren(
                latentComponents,
                deltaState.children,
                this.childContainer
            );

            // Clear everybody's position
            for (let childElement of this.childContainer
                .children as Iterable<HTMLElement>) {
                childElement.style.left = '0';
                childElement.style.top = '0';
            }
        }

        // Spacing
        if (deltaState.spacing !== undefined) {
            this.childContainer.style.gap = `${deltaState.spacing}rem`;
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

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth = 0;
        this.nGrowers = 0;
        // Add up all children's requested widths
        for (let child of this.children) {
            this.naturalWidth += child.requestedWidth;
            this.nGrowers += child.state['_grow_'][0] as any as number;
        }

        // Account for spacing
        this.naturalWidth +=
            Math.max(this.children.size - 1, 0) * this.state.spacing;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        let additionalSpace = this.allocatedWidth - this.naturalWidth;
        let additionalSpacePerGrower =
            this.nGrowers === 0 ? 0 : additionalSpace / this.nGrowers;

        for (let child of this.children) {
            child.allocatedWidth = child.requestedWidth;

            if (child.state['_grow_'][0]) {
                child.allocatedWidth += additionalSpacePerGrower;
            }
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        this.naturalHeight = 0;

        for (let child of this.children) {
            this.naturalHeight = Math.max(
                this.naturalHeight,
                child.requestedHeight
            );
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Is all allocated space used? Highlight any undefined space
        let additionalSpace = this.allocatedWidth - this.naturalWidth;

        if (this.nGrowers > 0 || Math.abs(additionalSpace) < 1e-6) {
            this.undef1.style.flexGrow = '0';
            this.undef2.style.flexGrow = '0';
        } else {
            // If there is no child elements make a single undefined space take
            // up everything. This way there is no unsightly disconnect between
            // the two.
            let element = this.element;

            if (element.children.length === 0) {
                this.undef1.style.flexGrow = '1';
                this.undef2.style.flexGrow = '0';
            } else {
                this.undef1.style.flexGrow = '1';
                this.undef2.style.flexGrow = '1';
            }

            console.log(
                `Warning: Component #${this.id} has ${
                    additionalSpace * pixelsPerRem
                }px of unused space`
            );
        }

        // Assign the allocated height to the children
        for (let child of this.children) {
            child.allocatedHeight = this.allocatedHeight;
        }
    }
}

export class ColumnComponent extends LinearContainer {
    createElement(): HTMLElement {
        let element = super.createElement();
        element.classList.add('rio-column');
        return element;
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth = 0;

        for (let child of this.children) {
            this.naturalWidth = Math.max(
                this.naturalWidth,
                child.requestedWidth
            );
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        // Assign the allocated width to the children
        for (let child of this.children) {
            child.allocatedWidth = this.allocatedWidth;
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        this.naturalHeight = 0;
        this.nGrowers = 0;

        // Add up all children's requested heights
        for (let child of this.children) {
            this.naturalHeight += child.requestedHeight;
            this.nGrowers += child.state['_grow_'][1] as any as number;
        }

        // Account for spacing
        this.naturalHeight +=
            Math.max(this.children.size - 1, 0) * this.state.spacing;
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Is all allocated space used? Highlight any undefined space
        let additionalSpace = this.allocatedHeight - this.naturalHeight;

        if (this.nGrowers > 0 || Math.abs(additionalSpace) < 1e-6) {
            this.undef1.style.flexGrow = '0';
            this.undef2.style.flexGrow = '0';
        } else {
            // If there is no child elements make a single undefined space take
            // up everything. This way there is no unsightly disconnect between
            // the two.
            let element = this.element;

            if (element.children.length === 0) {
                this.undef1.style.flexGrow = '1';
                this.undef2.style.flexGrow = '0';
            } else {
                this.undef1.style.flexGrow = '1';
                this.undef2.style.flexGrow = '1';
            }

            console.log(
                `Warning: Component #${this.id} has ${
                    additionalSpace * pixelsPerRem
                }px of unused space`
            );
        }

        // Assign the allocated height to the children
        let children = this.children;
        let additionalSpacePerGrower =
            this.nGrowers === 0 ? 0 : additionalSpace / this.nGrowers;

        for (let child of children) {
            child.allocatedHeight = child.requestedHeight;

            if (child.state['_grow_'][1]) {
                child.allocatedHeight += additionalSpacePerGrower;
            }
        }
    }
}
