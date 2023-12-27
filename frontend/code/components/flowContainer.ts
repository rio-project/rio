import { replaceChildren } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentBase, ComponentState } from './componentBase';

export type FlowState = ComponentState & {
    _type_: 'FlowContainer-builtin';
    children?: (number | string)[];
    spacing_x?: number;
    spacing_y?: number;
};

export class FlowComponent extends ComponentBase {
    state: Required<FlowState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-flow-container');
        return element;
    }

    updateElement(deltaState: FlowState): void {
        // Update the children
        replaceChildren(this.element.id, this.element, deltaState.children);

        // Update the layout
        this.makeLayoutDirty();
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth = 0;

        for (let child of this.getDirectChildren()) {
            this.naturalWidth = Math.max(
                this.naturalWidth,
                child.requestedWidth
            );
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        for (let child of this.getDirectChildren()) {
            child.allocatedWidth = child.requestedWidth;
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        // Allow the code below to assume there's at least one child
        let children = this.getDirectChildren();

        if (children.length === 0) {
            this.naturalHeight = 0;
            return;
        }

        // The height can only be known after a full layout of the children,
        // since multiple may share the same row.
        //
        // Layouting however, requires knowledge about the height of each row.
        // So before actually assigning positions, just assign everything into
        // abstract lines;
        let rows: ComponentBase[][] = [];
        let rowHeights: number[] = [];

        let posX = 0;
        let rowHeight = 0;
        let row: ComponentBase[] = [];

        for (let child of children) {
            // If the child is too wide, move on to the next row
            if (posX + child.requestedWidth > this.allocatedWidth) {
                posX = 0;

                rowHeights.push(rowHeight);
                rowHeight = 0;

                rows.push(row);
                row = [];
            }

            // Assign the child to the row
            row.push(child);

            // Update the row height
            rowHeight = Math.max(rowHeight, child.requestedHeight);

            // Lay out the component horizontally
            let elem = child.element;
            elem.style.left = `${posX}rem`;

            // Account for the spacing
            posX += child.requestedWidth;
            posX += this.state.spacing_x;
        }

        // Push the pending values
        rowHeights.push(rowHeight);
        rows.push(row);

        // Assign the children's heights and vertical positions
        let posY = 0;
        for (let ii = 0; ii < rows.length; ii++) {
            let row = rows[ii];
            let rowHeight = rowHeights[ii];

            for (let child of row) {
                let elem = child.element;
                elem.style.top = `${posY}rem`;

                child.allocatedHeight = rowHeight;
            }

            // Account for the spacing
            posY += rowHeight;
            posY += this.state.spacing_y;
        }

        // Now set the natural height. Take care to ignore the last spacing
        this.naturalHeight = posY - this.state.spacing_y;
    }

    updateAllocatedHeight(ctx: LayoutContext): void {}
}
