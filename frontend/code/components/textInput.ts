import { ComponentBase, ComponentState } from './componentBase';
// TODO

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

    private inputElement: HTMLInputElement;

    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add(
            'rio-text-input',
            'rio-input-box',
            'mdc-ripple-surface'
        );

        element.innerHTML = `
            <input type="text" style="order: 2" placeholder="">
            <div class="rio-input-box-hint-text rio-input-box-prefix-text" style="order: 1"></div>
            <div class="rio-input-box-hint-text rio-input-box-suffix-text" style="order: 3"></div>
            <div class="rio-input-box-label"></div>
            <div class="rio-input-box-plain-bar"></div>
            <div class="rio-input-box-color-bar"></div>
        `;

        // Detect value changes and send them to the backend
        this.inputElement = element.querySelector('input') as HTMLInputElement;

        this.inputElement.addEventListener('blur', () => {
            this.setStateAndNotifyBackend({
                text: this.inputElement.value,
            });
        });

        // Detect the enter key and send it to the backend
        //
        // In addition to notifying the backend, also include the input's
        // current value. This ensures any event handlers actually use the up-to
        // date value.
        this.inputElement.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                this.sendMessageToBackend({
                    text: this.inputElement.value,
                });
            }
        });

        // Detect clicks on any part of the component and focus the input
        element.addEventListener('click', () => {
            this.inputElement.focus();
        });

        return element;
    }

    updateElement(element: HTMLElement, deltaState: TextInputState): void {
        if (deltaState.text !== undefined) {
            this.inputElement.value = deltaState.text;
        }

        if (deltaState.label !== undefined) {
            let labelElement = element.querySelector(
                '.rio-input-box-label'
            ) as HTMLElement;
            labelElement.textContent = deltaState.label;

            // Adapt the minimum height, depending on whether there is a label
            if (deltaState.label.length > 0) {
                element.classList.add('rio-input-box-with-label');
            } else {
                element.classList.remove('rio-input-box-with-label');
            }
        }

        if (deltaState.prefix_text !== undefined) {
            let prefixElement = element.querySelector(
                '.rio-input-box-prefix-text'
            ) as HTMLElement;
            prefixElement.textContent = deltaState.prefix_text;
        }

        if (deltaState.suffix_text !== undefined) {
            let suffixElement = element.querySelector(
                '.rio-input-box-suffix-text'
            ) as HTMLElement;
            suffixElement.textContent = deltaState.suffix_text;
        }

        if (deltaState.is_secret !== undefined) {
            this.inputElement.type = deltaState.is_secret ? 'password' : 'text';
        }

        if (deltaState.is_sensitive === true) {
            this.inputElement.disabled = false;
            element.classList.remove('rio-disabled-input');
        } else if (deltaState.is_sensitive === false) {
            this.inputElement.disabled = true;
            element.classList.add('rio-disabled-input');
        }

        if (deltaState.is_valid === false) {
            element.style.setProperty(
                '--rio-local-text-color',
                'var(--rio-global-danger-bg)'
            );
        } else if (deltaState.is_valid === true) {
            element.style.removeProperty('--rio-local-text-color');
        }
    }

    grabKeyboardFocus(): void {
        this.inputElement.focus();
    }
}
