import { WidgetBase, WidgetState } from './widgetBase';
import { MDCTextField } from '@material/textfield';

export type DropdownState = WidgetState & {
    _type_: 'dropdown';
    optionNames?: string[];
    label?: string;
    selectedName?: string;
    is_sensitive?: boolean;
};

export function showPopup(popup: HTMLElement): void {
    popup.style.maxHeight = popup.scrollHeight + 'px';
}

export function hidePopup(popup: HTMLElement): void {
    popup.style.maxHeight = '0px';
}

export class DropdownWidget extends WidgetBase {
    state: Required<DropdownState>;

    private popupElement: HTMLElement;
    private optionsElement: HTMLElement;

    private mdcTextField: MDCTextField;

    createElement(): HTMLElement {
        // Create the elements
        let element = document.createElement('div');
        element.classList.add('reflex-dropdown');

        element.innerHTML = `
<label class="mdc-text-field mdc-text-field--filled">
    <span class="mdc-text-field__ripple"></span>
    <span class="mdc-floating-label"></span>
    <span class="mdc-text-field__affix mdc-text-field__affix--prefix"></span>
    <input class="mdc-text-field__input" type="text">
    <span class="mdc-text-field__affix mdc-text-field__affix--suffix"></span>
    <span class="mdc-line-ripple"></span>
    <div class=reflex-dropdown-obstruction></div>
</label>

<div class='reflex-popup'>
    <div class="reflex-dropdown-options"></div>
</div>
`;

        // Expose them as properties
        this.popupElement = element.querySelector(
            '.reflex-popup'
        ) as HTMLElement;

        this.optionsElement = element.querySelector(
            '.reflex-dropdown-options'
        ) as HTMLElement;

        let obstructionElement = element.querySelector(
            '.reflex-dropdown-obstruction'
        ) as HTMLElement;

        // Connect events
        let outsideClickListener = (event) => {
            // Check if the click was outside of the dropdown widget
            if (event.target === element || element.contains(event.target)) {
                return;
            }

            // Hide the popup
            hidePopup(this.popupElement);

            // De-register the event listener
            document.removeEventListener('click', outsideClickListener);
        };

        obstructionElement.addEventListener('click', () => {
            showPopup(this.popupElement);
            document.addEventListener('click', outsideClickListener);
        });

        // Initialize the material design component
        this.mdcTextField = new MDCTextField(element);

        return element;
    }

    updateElement(element: HTMLElement, deltaState: DropdownState): void {
        if (deltaState.optionNames !== undefined) {
            this.optionsElement.innerHTML = '';

            for (let optionName of deltaState.optionNames) {
                let optionElement = document.createElement('div');
                optionElement.classList.add('reflex-dropdown-option');
                optionElement.textContent = optionName;
                this.optionsElement.appendChild(optionElement);

                optionElement.addEventListener('click', () => {
                    hidePopup(this.popupElement);
                    this.mdcTextField.value = optionName;
                    this.sendMessageToBackend({
                        name: optionName,
                    });
                });
            }
        }

        if (deltaState.label !== undefined) {
            let child = element.querySelector(
                '.mdc-floating-label'
            ) as HTMLElement;
            child.textContent = deltaState.label;
        }

        if (deltaState.selectedName !== undefined) {
            this.mdcTextField.value = deltaState.selectedName;
        }

        if (deltaState.is_sensitive !== undefined) {
            this.mdcTextField.disabled = !deltaState.is_sensitive;
        }
    }
}
