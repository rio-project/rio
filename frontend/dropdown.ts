import { WidgetBase, WidgetState } from './widgetBase';

export type DropdownState = WidgetState & {
    _type_: 'dropdown';
    optionNames?: string[];
    selectedName?: string;
};

export class DropdownWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('select');
        element.classList.add('reflex-dropdown');

        element.addEventListener('input', () => {
            this.sendMessageToBackend({
                name: element.value,
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

        if (deltaState.selectedName !== undefined) {
            if (deltaState.selectedName === null) {
                (element as HTMLSelectElement).selectedIndex = -1;
            } else {
                (element as HTMLSelectElement).value = deltaState.selectedName;
            }
        }
    }
}
