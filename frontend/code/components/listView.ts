import { HtmlExtension } from 'micromark/lib/compile';
import { replaceChildrenAndResetCssProperties } from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type ListViewState = ComponentState & {
    children?: (number | string)[];
};

export class ListViewComponent extends ComponentBase {
    state: Required<ListViewState>;

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-list-view');
        return element;
    }

    _isGroupedListItem(element: HTMLElement): boolean {
        // Check whether the element has the `rio-custom-list-item` class.
        // However, take care to unwrap the outer div first.
        return !element.firstElementChild!.classList.contains(
            'rio-heading-list-item'
        );
    }

    _updateChildStyles(element: HTMLElement): void {
        // Round the corners of each first & last child in a a group, and add
        // separators between them.
        //
        // Make sure to work on a copy because the element will be modified by
        // the loop.
        for (let curChildUncast of Array.from(element.children)) {
            let curChild = curChildUncast as HTMLElement;

            // Make sure the element is a single container
            curChild.classList.add('rio-single-container');

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

            console.log(
                `EE
${prevChild?.firstElementChild?.classList} -> ${prevIsGrouped} (${prevChild})
${curChild.firstElementChild?.classList} -> ${curIsGrouped}
${nextChild?.firstElementChild?.classList} -> ${nextIsGrouped} (${nextChild})`
            );

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

    _updateElement(element: HTMLElement, deltaState: ListViewState): void {
        if (deltaState.children !== undefined) {
            // Update the children
            //
            // Wrap them all in helper divs, so any CSS properties can be
            // modified without having to worry. Destroying something important.
            replaceChildrenAndResetCssProperties(
                element.id,
                element,
                deltaState.children,
                true
            );

            // Update their CSS properties
            this._updateChildStyles(element);
        }
    }
}
