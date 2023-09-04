import { colorToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type SwitchState = WidgetState & {
    _type_: 'switch';
    is_on?: boolean;
};

export class SwitchWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-switch');

        let containerElement = document.createElement('div');
        containerElement.classList.add('container');
        element.appendChild(containerElement);

        let checkboxElement = document.createElement('input');
        checkboxElement.type = 'checkbox';
        containerElement.appendChild(checkboxElement);

        let knobElement = document.createElement('div');
        knobElement.classList.add('knob');
        containerElement.appendChild(knobElement);

        checkboxElement.addEventListener('change', () => {
            this.setStateAndNotifyBackend({
                is_on: checkboxElement.checked,
            });
        });

        return element;
    }

    updateElement(element: HTMLElement, deltaState: SwitchState): void {
        if (deltaState.is_on !== undefined) {
            if (deltaState.is_on) {
                element.classList.add('is-on');
            } else {
                element.classList.remove('is-on');
            }

            // Assign the new value to the checkbox element, but only if it
            // differs from the current value, to avoid immediately triggering
            // the event again.
            let checkboxElement = element.querySelector('input');
            if (checkboxElement?.checked !== deltaState.is_on) {
                checkboxElement!.checked = deltaState.is_on;
            }
        }
    }
}

