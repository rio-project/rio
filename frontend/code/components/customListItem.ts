import { SingleContainer } from './singleContainer';
import { MDCRipple } from '@material/ripple';
import { ComponentState } from './componentBase';

export type CustomListItemState = ComponentState & {
    _type_: 'CustomListItem-builtin';
    child?: number | string;
    pressable?: boolean;
};

export class CustomListItemComponent extends SingleContainer {
    state: Required<CustomListItemState>;

    // If this item has a ripple effect, this is the ripple instance. `null`
    // otherwise.
    private mdcRipple: MDCRipple | null = null;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-custom-list-item');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: CustomListItemState): void {
        // Style the surface depending on whether it is pressable.
        if (deltaState.pressable === true) {
            if (this.mdcRipple === null) {
                this.mdcRipple = new MDCRipple(element);

                element.classList.add(
                    'mdc-ripple-surface',
                    'rio-rectangle-ripple'
                );
                element.style.cursor = 'pointer';

                element.onclick = this._on_press.bind(this);
            }
        } else if (deltaState.pressable === false) {
            if (this.mdcRipple !== null) {
                this.mdcRipple.destroy();
                this.mdcRipple = null;

                element.classList.remove(
                    'mdc-ripple-surface',
                    'rio-rectangle-ripple'
                );
                element.style.removeProperty('cursor');

                element.onclick = null;
            }
        }

        // The ripple effect stores the coordinates of its rectangle. Since rio
        // likes to resize and move around components, the rectangle must be
        // updated appropriately.
        //
        // Really, this should be done when the component is resized or moved,
        // but there is no hook for that. Update seems to work fine.
        if (this.mdcRipple !== null) {
            requestAnimationFrame(() => {
                if (this.mdcRipple !== null) {
                    this.mdcRipple.layout();
                }
            });
        }
    }

    private _on_press(): void {
        this.sendMessageToBackend({
            type: 'press',
        });
    }
}
