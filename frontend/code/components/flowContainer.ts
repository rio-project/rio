import { replaceChildren } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentBase, ComponentState } from './componentBase';

// TODO
export type FlowState = ComponentState & {
    _type_: 'Flow-builtin';
    children?: (number | string)[];
    spacing?: number;
};

export class FlowComponent extends ComponentBase {
    state: Required<FlowState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-flow');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: FlowState): void {
        // Update the children
        replaceChildren(element.id, element, deltaState.children);

        // Spacing
        if (deltaState.spacing !== undefined) {
            element.style.gap = `${deltaState.spacing}rem`;
        }

        // Update the layout
        this.makeLayoutDirty();
    }

    updateRequestedWidth(ctx: LayoutContext): void {
        this.requestedWidth = 0;

        for (let child of ctx.directChildren(this)) {
            this.requestedWidth = Math.max(
                this.requestedWidth,
                child.requestedWidth
            );

            child.allocatedWidth = child.requestedWidth;
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {}

    updateRequestedHeight(ctx: LayoutContext): void {
        // The height can only be known after a full layout of the children,
        // since multiple may share the same row.
        //
        // Layouting however, requires knowledge about the height of each row.
        // So before actually assigning positions, just assign everything into
        // abstract lines;
        let lines: ComponentBase[][] = [];
        let lineHeights: number[] = [];

        let posX = 0;
        let lineHeight = 0;

        for (let child of ctx.directChildren(this)) {
            // If the child is too wide, move on to the next row
            let line;
            if (posX + child.requestedWidth > this.allocatedWidth) {
                posX = 0;

                lineHeights.push(lineHeight);
                lineHeight = 0;

                line = [];
                lines.push(line);
            } else if (lines.length > 0) {
                line = lines[lines.length - 1];
            } else {
                line = [];
                lines.push(line);
            }

            // Assign the child to the line
            line.push(child);

            // Lay out the component horizontally
            let elem = child.element();
            elem.style.left = `${posX}rem`;

            // Account for the spacing
            posX += child.requestedWidth;
            posX += this.state.spacing;
        }

        // Push the last line height
        if (lines.length > 0) {
            lineHeights.push(lineHeight);
        }

        // Assign the children's heights and vertical positions
        let posY = 0;
        for (let ii = 0; ii < lines.length; ii++) {
            let line = lines[ii];
            let lineHeight = lineHeights[ii];

            for (let child of line) {
                let elem = child.element();
                elem.style.top = `${posY}rem`;

                child.allocatedHeight = lineHeight;
            }

            // Account for the spacing
            posY += lineHeight;
            posY += this.state.spacing;
        }

        // Now set the requested height. Take care to ignore the last spacing
        this.requestedHeight =
            posY - lines.length === 0 ? 0 : this.state.spacing;
    }

    updateAllocatedHeight(ctx: LayoutContext): void {}
}
