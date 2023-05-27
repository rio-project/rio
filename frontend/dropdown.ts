import { WidgetBase, WidgetState } from './widgetBase';

export type DropdownState = WidgetState & {
    _type_: 'dropdown';
    optionNames?: string[];
};

export class DropdownWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('select');
        element.classList.add('reflex-dropdown');

        element.addEventListener('input', () => {
            this.setStateAndNotifyBackend({
                value: element.value,
            });
        });

        return element;
    }

    updateElement(element: HTMLElement, deltaState: DropdownState): void {
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
