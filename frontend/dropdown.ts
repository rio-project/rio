import { JsonDropdown } from './models';
import { sendEvent } from './app';

export class DropdownWidget {
    static build(): HTMLElement {
        let element = document.createElement('select');
        element.classList.add('reflex-dropdown');

        element.addEventListener('input', () => {
            sendEvent(element, 'dropdownChangeEvent', {
                value: element.value,
            });
        });

        return element;
    }

    static update(element: HTMLElement, deltaState: JsonDropdown): void {
        if (deltaState.optionNames !== undefined) {
            element.innerHTML = '';

            for (let optionName of deltaState.optionNames) {
                let option = document.createElement('option');
                option.value = optionName;
                option.text = optionName;
                element.appendChild(option);
            }
        }
    }
}
