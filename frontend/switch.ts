import { colorToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type SwitchState = WidgetState & {
    _type_: 'switch';
    is_on?: boolean;
    knobColorOn?: [number, number, number, number];
    knobColorOff?: [number, number, number, number];
    backgroundColorOn?: [number, number, number, number];
    backgroundColorOff?: [number, number, number, number];
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

            element.querySelector('input')!.checked = deltaState.is_on;
        }

        if (deltaState.knobColorOff !== undefined) {
            element.style.setProperty(
                '--switch-knob-color-off',
                colorToCss(deltaState.knobColorOff)
            );
        }

        if (deltaState.knobColorOn !== undefined) {
            element.style.setProperty(
                '--switch-knob-color-on',
                colorToCss(deltaState.knobColorOn)
            );
        }

        if (deltaState.backgroundColorOff !== undefined) {
            element.style.setProperty(
                '--switch-background-color-off',
                colorToCss(deltaState.backgroundColorOff)
            );
        }

        if (deltaState.backgroundColorOn !== undefined) {
            element.style.setProperty(
                '--switch-background-color-on',
                colorToCss(deltaState.backgroundColorOn)
            );
        }
    }
}
