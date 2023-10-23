import { applyColorSet } from '../designApplication';
import { ColorSet } from '../models';
import { ComponentState } from './componentBase';
import { MDCRipple } from '@material/ripple';
import { SingleContainer } from './singleContainer';

export type ButtonState = ComponentState & {
    _type_: 'Button-builtin';
    shape?: 'pill' | 'rounded' | 'rectangle' | 'circle';
    style?: 'major' | 'minor';
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

    _createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-button', 'mdc-ripple-surface');

        // Add a material ripple effect
        this.mdcRipple = new MDCRipple(element);

        // Detect button presses
        element.onmouseup = (e) => {
            // Do nothing if the button isn't sensitive
            if (!this.state['is_sensitive'] || this.isStillInitiallyDisabled) {
                return;
            }

            // Otherwise notify the backend
            this.sendMessageToBackend({
                type: 'press',
            });
        };

        requestAnimationFrame(() => {
            this.mdcRipple.layout();
        });

        return element;
    }

    onCreation(element: HTMLElement, state: Required<ButtonState>): void {
        setTimeout(() => {
            this.isStillInitiallyDisabled = false;
        }, state.initially_disabled_for * 1000);
    }

    _updateElement(element: HTMLElement, deltaState: ButtonState): void {
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
                'rio-buttonstyle-minor'
            );

            let className = 'rio-buttonstyle-' + deltaState.style;
            element.classList.add(className);
        }

        // Apply the color
        if (
            deltaState.color !== undefined ||
            deltaState.is_sensitive !== undefined
        ) {
            // It looks ugly if every new button is initially greyed out, so
            // for the styling we ignore `self.isStillInitiallyDisabled`.
            let is_sensitive: boolean =
                deltaState.is_sensitive || this.state['is_sensitive'];

            let colorSet = is_sensitive
                ? deltaState.color || this.state['color']
                : 'disabled';

            if (colorSet === 'keep') {
                colorSet = 'accent-to-plain';
            }

            applyColorSet(element, colorSet);
        }

        // The ripple stores the coordinates of its rectangle. Since rio likes
        // to resize and move around components, the rectangle must be updated
        // appropriately.
        //
        // Really, this should be done when the component is resized or moved,
        // but there is no hook for that. Update seems to work fine for now.
        requestAnimationFrame(() => {
            this.mdcRipple.layout();
        });
    }
}
