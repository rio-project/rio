import { applyColorSet } from '../designApplication';
import { ColorSet } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { MDCRipple } from '@material/ripple';
import { replaceOnlyChild } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { SingleContainer } from './singleContainer';

export type ButtonState = ComponentState & {
    _type_: 'Button-builtin';
    shape?: 'pill' | 'rounded' | 'rectangle';
    style?: 'major' | 'minor' | 'plain';
    color?: ColorSet;
    child?: number | string;
    is_sensitive?: boolean;
    initially_disabled_for?: number;
};

export class ButtonComponent extends SingleContainer {
    state: Required<ButtonState>;
    private mdcRipple: MDCRipple;

    // In order to prevent a newly created button from being clicked on
    // accident, it starts out disabled and enables itself after a short delay.
    private isStillInitiallyDisabled: boolean = true;

    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-button', 'mdc-ripple-surface');

        // Add a material ripple effect
        this.mdcRipple = new MDCRipple(element);

        // Detect button presses
        element.onmouseup = (event) => {
            event.stopPropagation();

            // Only react to left clicks
            if (event.button !== 0) {
                return;
            }

            // Do nothing if the button isn't sensitive
            if (!this.state['is_sensitive'] || this.isStillInitiallyDisabled) {
                return;
            }

            // Otherwise notify the backend
            this.sendMessageToBackend({
                type: 'press',
            });
        };

        return element;
    }

    onCreation(element: HTMLElement, state: Required<ButtonState>): void {
        setTimeout(() => {
            this.isStillInitiallyDisabled = false;
        }, state.initially_disabled_for * 1000);
    }

    updateElement(element: HTMLElement, deltaState: ButtonState): void {
        // Update the child
        if (deltaState.child !== undefined) {
            replaceOnlyChild(element.id, element, deltaState.child);
            this.makeLayoutDirty();
        }

        // Set the shape
        if (deltaState.shape !== undefined) {
            element.classList.remove(
                'rio-shape-pill',
                'rio-shape-rounded',
                'rio-shape-rectangle',
                'rio-shape-circle'
            );

            let className = 'rio-shape-' + deltaState.shape;
            element.classList.add(className);
        }

        // Set the style
        if (deltaState.style !== undefined) {
            element.classList.remove(
                'rio-buttonstyle-major',
                'rio-buttonstyle-minor',
                'rio-buttonstyle-plain'
            );

            let className = 'rio-buttonstyle-' + deltaState.style;
            element.classList.add(className);
        }

        // Apply the color
        if (
            deltaState.color !== undefined ||
            deltaState.is_sensitive !== undefined ||
            deltaState.style !== undefined
        ) {
            // It looks ugly if every new button is initially greyed out, so for
            // the styling ignore `self.isStillInitiallyDisabled`.
            let is_sensitive: boolean =
                deltaState.is_sensitive || this.state['is_sensitive'];

            let colorSet = is_sensitive
                ? deltaState.color || this.state['color']
                : 'disabled';

            let style = deltaState.style || this.state['style'];

            // If no new colorset is specified, turn the accent color into the
            // plain color. This allows all styles to just assume that the color
            // they should use is the plain color.
            //
            // The exception to this is the plain style, which obviously isn't
            // trying to stand out.
            if (colorSet === 'keep') {
                colorSet = 'accent-to-plain';
            }

            applyColorSet(element, colorSet);
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        super.updateAllocatedHeight(ctx);

        // The ripple stores the coordinates of its rectangle. Since Rio likes
        // to resize and move around components, the rectangle must be updated
        // appropriately.
        this.mdcRipple.layout();
    }
}
