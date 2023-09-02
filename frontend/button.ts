import { replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type ButtonState = WidgetState & {
    _type_: 'Button-builtin';
    shape: 'rounded' | 'rectangular' | 'circle';
    child?: number | string;
    is_major: boolean;
    is_sensitive: boolean;
};

export class ButtonWidget extends WidgetBase {
    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('reflex-button');
        element.classList.add('reflex-single-container');
        element.classList.add('mdc-ripple-surface');
        element.classList.add('mdc-ripple-surface--primary');

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

        return element;
    }

    updateElement(element: HTMLElement, deltaState: ButtonState): void {
        replaceOnlyChild(element, deltaState.child);

        // Set the style
        if (deltaState.is_major == true) {
            element.classList.add('reflex-buttonstyle-major');
            element.classList.remove('reflex-buttonstyle-minor');
        } else if (deltaState.is_major == false) {
            element.classList.add('reflex-buttonstyle-minor');
            element.classList.remove('reflex-buttonstyle-major');
        }

        // Set the shape
        if (deltaState.shape !== undefined) {
            element.classList.remove(
                'reflex-shape-rounded',
                'reflex-shape-rectangular',
                'reflex-shape-circle'
            );

            let className = 'reflex-shape-' + deltaState.shape;
            element.classList.add(className);
        }

        // Switch the style based on sensitivity
        if (deltaState.is_sensitive === true) {
            element.classList.remove('reflex-switcheroo-disabled');
        } else if (deltaState.is_sensitive === false) {
            element.classList.add('reflex-switcheroo-disabled');
        }
    }
}
