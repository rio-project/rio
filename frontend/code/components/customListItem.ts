import { MDCRipple } from '@material/ripple';
import { ComponentBase, ComponentState } from './componentBase';
import { componentsById } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';

const PADDING_X: number = 1.5;
const PADDING_Y: number = 0.7;

export type CustomListItemState = ComponentState & {
    _type_: 'CustomListItem-builtin';
    child?: ComponentId;
    pressable?: boolean;
};

export class CustomListItemComponent extends ComponentBase {
    state: Required<CustomListItemState>;

    // If this item has a ripple effect, this is the ripple instance. `null`
    // otherwise.
    private mdcRipple: MDCRipple | null = null;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-custom-list-item');
        return element;
    }

    updateElement(
        deltaState: CustomListItemState,
        latentComponents: Set<ComponentBase>
    ): void {
        // Update the child
        this.replaceOnlyChild(latentComponents, deltaState.child);

        // Style the surface depending on whether it is pressable.
        if (deltaState.pressable === true) {
            if (this.mdcRipple === null) {
                this.mdcRipple = new MDCRipple(this.element);

                this.element.classList.add(
                    'mdc-ripple-surface',
                    'rio-rectangle-ripple'
                );
                this.element.style.cursor = 'pointer';

                this.element.onclick = this._on_press.bind(this);
            }
        } else if (deltaState.pressable === false) {
            if (this.mdcRipple !== null) {
                this.mdcRipple.destroy();
                this.mdcRipple = null;

                this.element.classList.remove(
                    'mdc-ripple-surface',
                    'rio-rectangle-ripple'
                );
                this.element.style.removeProperty('cursor');

                this.element.onclick = null;
            }
        }
    }

    private _on_press(): void {
        this.sendMessageToBackend({
            type: 'press',
        });
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth =
            componentsById[this.state.child]!.requestedWidth + PADDING_X * 2;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        componentsById[this.state.child]!.allocatedWidth =
            this.allocatedWidth - PADDING_X * 2;
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        this.naturalHeight =
            componentsById[this.state.child]!.requestedHeight + PADDING_Y * 2;
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        let child = componentsById[this.state.child]!;
        child.allocatedHeight = this.allocatedHeight - PADDING_Y * 2;

        // Position the child
        let element = child.element;
        element.style.left = `${PADDING_X}rem`;
        element.style.top = `${PADDING_Y}rem`;

        // The ripple effect stores the coordinates of its rectangle. Since rio
        // likes to resize and move around components, the rectangle must be
        // updated appropriately.
        if (this.mdcRipple !== null) {
            this.mdcRipple.layout();
        }
    }
}
