import { ComponentBase, ComponentState } from './componentBase';

export type TextInputState = ComponentState & {
    _type_: 'textInput';
    text?: string;
    label?: string;
    prefix_text?: string;
    suffix_text?: string;
    is_secret?: boolean;
    is_sensitive?: boolean;
    is_valid?: boolean;
};

export class TextInputComponent extends ComponentBase {
    state: Required<TextInputState>;

    _createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-text-input');
        element.classList.add('mdc-ripple-surface');

        element.innerHTML = `
            <input type="text" style="order: 2" placeholder="">
            <div class="rio-text-input-hint-text rio-text-input-prefix-text" style="order: 1"></div>
            <div class="rio-text-input-hint-text rio-text-input-suffix-text" style="order: 3"></div>
            <div class="rio-text-input-label"></div>
            <div class="rio-text-input-color-bar"></div>
        `;

        // Detect value changes and send them to the backend
        let inputElement = element.querySelector('input') as HTMLInputElement;

        inputElement.addEventListener('blur', () => {
            this.setStateAndNotifyBackend({
                text: inputElement.value,
            });
        });

        // Detect the enter key and send it to the backend

        // In addition to notifying the backend, also include the input's
        // current value. This ensures any event handlers actually use the up-to
        // date value.
        inputElement.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                this.sendMessageToBackend({
                    text: inputElement.value,
                });
            }
        });

        return element;
    }

    _updateElement(element: HTMLElement, deltaState: TextInputState): void {
        let inputElement = element.querySelector('input') as HTMLInputElement;

        if (deltaState.text !== undefined) {
            inputElement.value = deltaState.text;
        }

        if (deltaState.label !== undefined) {
            let labelElement = element.querySelector(
                '.rio-text-input-label'
            ) as HTMLElement;
            labelElement.textContent = deltaState.label;

            // Adapt th minimum height, depending on whether there is a label
            element.style.minHeight =
                deltaState.label.length > 0 ? '3.3rem' : '2.3rem';
        }

        if (deltaState.prefix_text !== undefined) {
            let prefixElement = element.querySelector(
                '.rio-text-input-prefix-text'
            ) as HTMLElement;
            prefixElement.textContent = deltaState.prefix_text;
        }

        if (deltaState.suffix_text !== undefined) {
            let suffixElement = element.querySelector(
                '.rio-text-input-suffix-text'
            ) as HTMLElement;
            suffixElement.textContent = deltaState.suffix_text;
        }

        if (deltaState.is_secret !== undefined) {
            inputElement.type = deltaState.is_secret ? 'password' : 'text';
        }

        if (deltaState.is_sensitive === true) {
            inputElement.disabled = false;
            element.classList.remove('rio-disabled-input');
        } else if (deltaState.is_sensitive === false) {
            inputElement.disabled = true;
            element.classList.add('rio-disabled-input');
        }

        if (deltaState.is_valid === false) {
            element.style.setProperty(
                '--rio-local-text-color',
                'var(--rio-global-danger-color)'
            );
        } else if (deltaState.is_valid === true) {
            element.style.removeProperty('--rio-local-text-color');
        }
    }
}
