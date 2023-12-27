import { replaceChildren } from '../componentManagement';
import { ColumnComponent, LinearContainerState } from './linearContainers';

export class ListViewComponent extends ColumnComponent {
    constructor(elementId: string, state: Required<LinearContainerState>) {
        state.spacing = 0;
        super(elementId, state);
    }

    createElement(): HTMLElement {
        let element = super.createElement();
        element.classList.add('rio-list-view');
        return element;
    }

    updateElement(deltaState: LinearContainerState): void {
        // Columns don't wrap their children in divs, but ListView does. Hence
        // the overridden createElement.
        replaceChildren(
            this.element.id,
            this.childContainer,
            deltaState.children,
            true
        );

        // Clear everybody's position
        for (let child of this.childContainer.children) {
            let element = child.firstElementChild as HTMLElement;
            element.style.left = '0';
            element.style.top = '0';
        }

        // Update the styles of the children
        this._updateChildStyles();

        // Update the layout
        this.makeLayoutDirty();
    }

    _isGroupedListItem(element: HTMLElement): boolean {
        // Check whether the element has the `rio-custom-list-item` class.
        // However, take care to unwrap the outer div first.
        return !element.firstElementChild!.classList.contains(
            'rio-heading-list-item'
        );
    }

    _updateChildStyles(): void {
        // Round the corners of each first & last child in a a group, and add
        // separators between them.
        //
        // Make sure to work on a copy because the element will be modified by
        // the loop.
        for (let curChildUncast of Array.from(this.childContainer.children)) {
            let curChild = curChildUncast as HTMLElement;

            // Is this even a regular list item?
            let curIsGrouped = this._isGroupedListItem(curChild);

            // Look up the neighboring elements
            let prevChild = curChild.previousElementSibling;
            let nextChild = curChild.nextElementSibling;

            let prevIsGrouped =
                prevChild !== null &&
                this._isGroupedListItem(prevChild as HTMLElement);
            let nextIsGrouped =
                nextChild !== null &&
                this._isGroupedListItem(nextChild as HTMLElement);

            if (!curIsGrouped) {
                continue;
            }

            // Round the corners
            let topRadius = prevIsGrouped
                ? '0'
                : 'var(--rio-global-corner-radius-small)';
            let bottomRadius = nextIsGrouped
                ? '0'
                : 'var(--rio-global-corner-radius-small)';

            curChild.style.borderTopLeftRadius = topRadius;
            curChild.style.borderTopRightRadius = topRadius;
            curChild.style.borderBottomLeftRadius = bottomRadius;
            curChild.style.borderBottomRightRadius = bottomRadius;

            curChild.style.overflow = 'hidden';

            // Add a separator? These have to be discrete elements, because CSS
            // doesn't support setting opacity of a color defined in a variable
            if (prevIsGrouped) {
                let separator = document.createElement('div');
                separator.classList.add('rio-separator');
                curChild.insertBefore(separator, curChild.firstElementChild);
            }
        }
    }
}
