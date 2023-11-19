import {
    getElementByComponentId,
    replaceChildrenAndResetCssProperties,
} from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

type GridChildPosition = {
    row: number;
    column: number;
    width: number;
    height: number;
};

export type GridState = ComponentState & {
    _type_: 'Grid';
    _children?: (number | string)[];
    _child_positions?: GridChildPosition[];
    row_spacing?: number;
    column_spacing?: number;
};

export class GridComponent extends ComponentBase {
    state: Required<GridState>;

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-grid');
        return element;
    }

    _updateElement(element: HTMLElement, deltaState: GridState): void {
        replaceChildrenAndResetCssProperties(
            element.id,
            element,
            deltaState._children
        );

        if (deltaState.row_spacing !== undefined) {
            element.style.rowGap = `${deltaState.row_spacing}em`;
        }

        if (deltaState.column_spacing !== undefined) {
            element.style.columnGap = `${deltaState.column_spacing}em`;
        }
    }

    updateChildLayouts(): void {
        this.state._children!.forEach((childId, index) => {
            let childPosition = this.state._child_positions![index];
            let childElement = getElementByComponentId(childId);

            childElement.style.gridRowStart = `${childPosition.row + 1}`;
            childElement.style.gridRowEnd = `${
                childPosition.row + 1 + childPosition.height
            }`;

            childElement.style.gridColumnStart = `${childPosition.column + 1}`;
            childElement.style.gridColumnEnd = `${
                childPosition.column + 1 + childPosition.width
            }`;
        });
    }
}
