import { SingleContainer } from './singleContainer';
import { MDCRipple } from '@material/ripple';
import { ComponentState } from './componentBase';

export type ListItemState = ComponentState & {
    _type_: 'ListItem-builtin';
    child?: number | string;
    pressable?: boolean;
};

export class ListItemComponent extends SingleContainer {
    state: Required<ListItemState>;

    // If this item has a ripple effect, this is the ripple instance. `null`
    // otherwise.
    private mdcRipple: MDCRipple | null = null;

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-list-item');
        return element;
    }

    _updateElement(element: HTMLElement, deltaState: ListItemState): void {
        // Style the surface depending on whether it is pressable.
        if (deltaState.pressable === true) {
            if (this.mdcRipple === null) {
                this.mdcRipple = new MDCRipple(element);

                element.classList.add('mdc-ripple-surface');
                element.classList.add('rio-rectangle-ripple');
            }
        } else if (deltaState.pressable === false) {
            if (this.mdcRipple !== null) {
                this.mdcRipple.destroy();
                this.mdcRipple = null;

                element.classList.remove('mdc-ripple-surface');
                element.classList.remove('rio-rectangle-ripple');
            }
        }

        // The ripple effect stores the coordinates of its rectangle. Since
        // rio likes to resize and move around components, the rectangle must be
        // updated appropriately.
        //
        // Really, this should be done when the component is resized or moved, but
        // there is no hook for that. Update seems to work fine.
        if (this.mdcRipple !== null) {
            requestAnimationFrame(() => {
                if (this.mdcRipple !== null) {
                    this.mdcRipple.layout();
                }
            });
        }
    }
}
