import { JsonSwitch } from './models';
import { sendEvent } from './app';


export class SwitchWidget {
    static build(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-switch');

        element.addEventListener('click', () => {
            sendEvent(element, 'switchChangeEvent', {
                isOn: element.textContent !== 'true',
            });
        });

        return element;
    }

    static update(element: HTMLElement, deltaState: JsonSwitch): void {
        if (deltaState.is_on !== undefined) {
            element.textContent = deltaState.is_on.toString();
            element.style.backgroundColor = deltaState.is_on ? 'green' : 'red';
        }
    }
}
