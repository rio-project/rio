import { replaceOnlyChild } from '../widgetManagement';
import { applyColorSet } from '../designApplication';
import { ColorSet } from '../models';
import { WidgetBase, WidgetState } from './widgetBase';
import { MDCRipple } from '@material/ripple';

export type ButtonState = WidgetState & {
    _type_: 'Button-builtin';
    shape: 'pill' | 'rounded' | 'rectangle' | 'circle';
    style: 'major' | 'minor';
    color: ColorSet;
    child?: number | string;
    is_sensitive: boolean;
};

export class ButtonWidget extends WidgetBase {
    state: Required<ButtonState>;
    private mdcRipple: MDCRipple;

    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-button');
        element.classList.add('rio-single-container');
        element.classList.add('mdc-ripple-surface');

        // Add a material ripple effect
        this.mdcRipple = new MDCRipple(element);

        // Detect button presses
        element.onmouseup = (e) => {
            // Do nothing if the button isn't sensitive
            if (!this.state['is_sensitive']) {
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

    updateElement(element: HTMLElement, deltaState: ButtonState): void {
        replaceOnlyChild(element, deltaState.child);

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
        let is_sensitive: boolean =
            deltaState.is_sensitive || this.state['is_sensitive'];

        let colorSet = is_sensitive ? deltaState.color : 'disabled';

        if (colorSet !== undefined) {
            applyColorSet(element, colorSet);
        }

        // The slider stores the coordinates of its rectangle. Since rio
        // likes to resize and move around widgets, the rectangle must be
        // updated appropriately.
        //
        // Really, this should be done when the widget is resized or moved, but
        // there is no hook for that. Update seems to work fine.
        requestAnimationFrame(() => {
            this.mdcRipple.layout();
        });
    }
}
