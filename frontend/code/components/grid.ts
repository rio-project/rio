import {
    getElementByComponentId,
    getInstanceByComponentId,
    replaceChildren,
} from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { range } from '../utils';
import { ComponentBase, ComponentState } from './componentBase';

type GridChildPosition = {
    row: number;
    column: number;
    width: number;
    height: number;
};

type GridChild = {
    id: ComponentId;
    allRows: number[];
    allColumns: number[];
} & GridChildPosition;

export type GridState = ComponentState & {
    _type_: 'Grid-builtin';
    _children?: ComponentId[];
    _child_positions?: GridChildPosition[];
    row_spacing?: number;
    column_spacing?: number;
};

export class GridComponent extends ComponentBase {
    state: Required<GridState>;

    private childrenByNumberOfColumns: GridChild[];
    private childrenByNumberOfRows: GridChild[];

    private growingRows: Set<number>;
    private growingColumns: Set<number>;

    private nRows: number;
    private nColumns: number;

    private rowHeights: number[];
    private columnWidths: number[];

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-grid');
        return element;
    }

    precomputeChildData(deltaState: GridState): void {
        let children = deltaState._children as ComponentId[];

        // Build the list of grid childs
        for (let ii = 0; ii < children.length; ii++) {
            let child = deltaState._child_positions![ii] as GridChild;
            child.id = children[ii];
        }

        // Sort the children by the number of rows they take up
        this.childrenByNumberOfRows = Array.from(
            deltaState._child_positions!
        ) as GridChild[];
        this.childrenByNumberOfRows.sort((a, b) => a.height - b.height);

        this.nRows = 0;
        this.growingRows = new Set();

        for (let gridChild of this.childrenByNumberOfRows) {
            let childInstance = getInstanceByComponentId(gridChild.id);

            // Keep track of how how many rows this grid has
            this.nRows = Math.max(this.nRows, gridChild.row + gridChild.height);

            // Initialize the rows & columns stored in the child
            gridChild.allRows = range(
                gridChild.row,
                gridChild.row + gridChild.height
            );

            // Determine which rows need to grow
            if (!childInstance.state._grow_[1]) {
                continue;
            }

            // Does any of the rows already grow?
            let alreadyGrowing = gridChild.allRows.some((row) =>
                this.growingRows.has(row)
            );

            // If not, mark them all as growing
            if (!alreadyGrowing) {
                for (let row of gridChild.allRows) {
                    this.growingRows.add(row);
                }
            }
        }

        // Sort the children by the number of columns they take up
        this.childrenByNumberOfColumns = Array.from(
            this.childrenByNumberOfRows
        );
        this.childrenByNumberOfColumns.sort((a, b) => a.width - b.width);

        this.nColumns = 0;
        this.growingColumns = new Set();

        for (let gridChild of this.childrenByNumberOfColumns) {
            let childInstance = getInstanceByComponentId(gridChild.id);

            // Keep track of how how many columns this grid has
            this.nColumns = Math.max(
                this.nColumns,
                gridChild.column + gridChild.width
            );

            // Initialize the rows & columns stored in the child
            gridChild.allColumns = range(
                gridChild.column,
                gridChild.column + gridChild.width
            );

            // Determine which columns need to grow
            if (!childInstance.state._grow_[0]) {
                continue;
            }

            // Does any of the columns already grow?
            let alreadyGrowing = gridChild.allColumns.some((column) =>
                this.growingColumns.has(column)
            );

            // If not, mark them all as growing
            if (!alreadyGrowing) {
                for (let column of gridChild.allColumns) {
                    this.growingColumns.add(column);
                }
            }
        }
    }

    updateElement(element: HTMLElement, deltaState: GridState): void {
        if (deltaState._children !== undefined) {
            replaceChildren(element.id, element, deltaState._children);
            this.precomputeChildData(deltaState);
            this.updateChildLayouts();
        }

        if (deltaState.row_spacing !== undefined) {
            element.style.rowGap = `${deltaState.row_spacing}em`;
        }

        if (deltaState.column_spacing !== undefined) {
            element.style.columnGap = `${deltaState.column_spacing}em`;
        }

        this.makeLayoutDirty();
    }

    updateChildLayouts(): void {
        for (let gridChild of this.childrenByNumberOfRows) {
            let childElement = getElementByComponentId(gridChild.id);

            childElement.style.gridRowStart = `${gridChild.row + 1}`;
            childElement.style.gridRowEnd = `${
                gridChild.row + 1 + gridChild.height
            }`;

            childElement.style.gridColumnStart = `${gridChild.column + 1}`;
            childElement.style.gridColumnEnd = `${
                gridChild.column + 1 + gridChild.width
            }`;

            childElement.style.left = '0';
            childElement.style.top = '0';
        }
    }

    updateRequestedWidth(ctx: LayoutContext): void {
        this.columnWidths = new Array(this.nColumns).fill(0);

        // Determine the width of each column
        for (let gridChild of this.childrenByNumberOfColumns) {
            let childInstance = ctx.inst(gridChild.id);

            // How much of the child's width can the columns already accommodate?
            let availableWidthTotal: number =
                (gridChild.width - 1) * this.state.column_spacing;
            let growCols: number[] = [];

            for (let ii of gridChild.allColumns) {
                let columnWidth = this.columnWidths[ii];

                availableWidthTotal += columnWidth;
                if (this.growingColumns.has(ii)) {
                    growCols.push(ii);
                }
            }

            let neededSpace =
                childInstance.requestedWidth - availableWidthTotal;

            // The columns have enough free space
            if (neededSpace <= 0) {
                continue;
            }

            // Expand the columns
            let targetColumns =
                growCols.length > 0 ? growCols : gridChild.allColumns;

            let spacePerColumn = neededSpace / targetColumns.length;

            for (let column of targetColumns) {
                this.columnWidths[column] += spacePerColumn;
            }
        }

        // Sum over all widths
        this.requestedWidth = this.columnWidths.reduce(
            (a, b) => a + b + this.state.column_spacing,
            -this.state.column_spacing
        );
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        // Determine the width of each column
        let additionalSpace = this.allocatedWidth - this.requestedWidth;
        let targetColumns =
            this.growingColumns.size > 0
                ? this.growingColumns
                : new Set(range(0, this.nColumns));

        let spacePerColumn = additionalSpace / targetColumns.size;

        for (let column of targetColumns) {
            this.columnWidths[column] += spacePerColumn;
        }

        // Pass on the space to the children
        for (let gridChild of this.childrenByNumberOfColumns) {
            let childInstance = ctx.inst(gridChild.id);
            childInstance.allocatedWidth = 0;

            for (let column of gridChild.allColumns) {
                childInstance.allocatedWidth += this.columnWidths[column];
            }
        }
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        this.rowHeights = new Array(this.nRows).fill(0);

        // Determine the height of each row
        for (let gridChild of this.childrenByNumberOfRows) {
            let childInstance = ctx.inst(gridChild.id);

            // How much of the child's height can the rows already accommodate?
            let availableHeightTotal: number =
                (gridChild.height - 1) * this.state.row_spacing;
            let growRows: number[] = [];

            for (let ii of gridChild.allRows) {
                let rowHeight = this.rowHeights[ii];

                availableHeightTotal += rowHeight;
                if (this.growingRows.has(ii)) {
                    growRows.push(ii);
                }
            }

            let neededSpace =
                childInstance.requestedHeight - availableHeightTotal;

            // The rows have enough free space
            if (neededSpace <= 0) {
                continue;
            }

            // Expand the rows
            let targetRows = growRows.length > 0 ? growRows : gridChild.allRows;

            let spacePerRow = neededSpace / targetRows.length;

            for (let row of targetRows) {
                this.rowHeights[row] += spacePerRow;
            }
        }

        // Sum over all heights
        this.requestedHeight = this.rowHeights.reduce(
            (a, b) => a + b + this.state.row_spacing,
            -this.state.row_spacing
        );
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Determine the height of each row
        let additionalSpace = this.allocatedHeight - this.requestedHeight;
        let targetRows =
            this.growingRows.size > 0
                ? this.growingRows
                : new Set(range(0, this.nRows));

        let spacePerRow = additionalSpace / targetRows.size;

        for (let row of targetRows) {
            this.rowHeights[row] += spacePerRow;
        }

        // Precompute position data
        let columnWidthCumSum: number[] = [0];
        for (let columnWidth of this.columnWidths) {
            columnWidthCumSum.push(
                columnWidthCumSum[columnWidthCumSum.length - 1] +
                    columnWidth +
                    this.state.column_spacing
            );
        }

        let rowHeightCumSum: number[] = [0];
        for (let rowHeight of this.rowHeights) {
            rowHeightCumSum.push(
                rowHeightCumSum[rowHeightCumSum.length - 1] +
                    rowHeight +
                    this.state.row_spacing
            );
        }

        // Pass on the space to the children
        for (let gridChild of this.childrenByNumberOfRows) {
            let childInstance = ctx.inst(gridChild.id);
            childInstance.allocatedHeight = 0;

            for (let row of gridChild.allRows) {
                childInstance.allocatedHeight += this.rowHeights[row];
            }

            // Set everybody's position
            let childElement = getElementByComponentId(gridChild.id);

            childElement.style.left = `${
                columnWidthCumSum[gridChild.column]
            }rem`;
            childElement.style.top = `${rowHeightCumSum[gridChild.row]}rem`;
        }
    }
}
