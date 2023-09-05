import { getElementByWidgetId, replaceChildren } from './app';
import { WidgetBase, WidgetState } from './widgetBase';


type GridChildPosition = {
    row: number;
    column: number;
    width: number;
    height: number;
}


export type GridState = WidgetState & {
    _type_: 'Grid';
    _children?: (number | string)[];
    _child_positions?: GridChildPosition[];
    row_spacing?: number;
    column_spacing?: number;
};


export class GridWidget extends WidgetBase {
    state: GridState;
    
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-grid');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: GridState): void {
        replaceChildren(element, deltaState._children);

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
            let childElement = getElementByWidgetId(childId);

            childElement.style.gridRowStart = `${childPosition.row + 1}`;
            childElement.style.gridRowEnd = `${childPosition.row + 1 + childPosition.height}`;

            childElement.style.gridColumnStart = `${childPosition.column + 1}`;
            childElement.style.gridColumnEnd = `${childPosition.column + 1 + childPosition.width}`;
        });
    }
}
