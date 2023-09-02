import { WidgetBase, WidgetState } from './widgetBase';
import { MDCTextField } from '@material/textfield';

export type TextInputState = WidgetState & {
    _type_: 'textInput';
    text?: string;
    placeholder?: string;
    prefix_text?: string;
    suffix_text?: string;
    secret?: boolean;
    is_sensitive?: boolean;
};

export class TextInputWidget extends WidgetBase {
    private mdcTextField: MDCTextField;

    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('label');
        element.classList.add('mdc-text-field');
        element.classList.add('mdc-text-field--filled');

        element.innerHTML = `
  <span class="mdc-text-field__ripple"></span>
  <span class="mdc-floating-label"></span>
  <span class="mdc-text-field__affix mdc-text-field__affix--prefix"></span>
  <input class="mdc-text-field__input" type="text">
  <span class="mdc-text-field__affix mdc-text-field__affix--suffix"></span>
  <span class="mdc-line-ripple"></span>
`;

        // Initialize the material design component
        this.mdcTextField = new MDCTextField(element);

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

    updateElement(element: HTMLElement, deltaState: TextInputState): void {
        if (deltaState.text !== undefined) {
            this.mdcTextField.value = deltaState.text;
        }

        if (deltaState.placeholder !== undefined) {
            let child = element.querySelector(
                '.mdc-floating-label'
            ) as HTMLElement;
            child.textContent = deltaState.placeholder;
        }

        if (deltaState.prefix_text !== undefined) {
            this.mdcTextField.prefixText = deltaState.prefix_text;
        }

        if (deltaState.suffix_text !== undefined) {
            this.mdcTextField.suffixText = deltaState.suffix_text;
        }

        if (deltaState.secret !== undefined) {
            let input = element.querySelector('input') as HTMLInputElement;
            input.type = deltaState.secret ? 'password' : 'text';
        }

        if (deltaState.is_sensitive !== undefined) {
            this.mdcTextField.disabled = !deltaState.is_sensitive;
        }
    }
}
