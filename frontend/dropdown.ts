import { WidgetBase, WidgetState } from './widgetBase';

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
    private textInputElement: HTMLElement;
    private inputElement: HTMLInputElement;

    createElement(): HTMLElement {
        // Create the elements
        let element = document.createElement('div');
        element.classList.add('reflex-dropdown');
        element.classList.add('mdc-ripple-surface');

        element.innerHTML = `
        <div class="reflex-text-input">
            <input type="text" placeholder="" style="pointer-events: none" disabled>
            <div class="reflex-text-input-label"></div>
            <div class="reflex-text-input-color-bar"></div>
            <div class="reflex-icon-revealer-arrow"></div>
        </div>

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

        this.textInputElement = element.querySelector(
            '.reflex-text-input'
        ) as HTMLElement;

        this.inputElement = element.querySelector('input') as HTMLInputElement;

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

        this.textInputElement.addEventListener('click', () => {
            console.log('click');
            showPopup(this.popupElement);
            document.addEventListener('click', outsideClickListener);
        });

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
                    this.inputElement.value = optionName;
                    this.sendMessageToBackend({
                        name: optionName,
                    });
                });
            }
        }

        if (deltaState.label !== undefined) {
            let labelElement = element.querySelector(
                '.reflex-text-input-label'
            ) as HTMLElement;
            labelElement.textContent = deltaState.label;

            // Adapt th minimum height, depending on whether there is a label
            this.textInputElement.style.minHeight =
                deltaState.label.length > 0 ? '3.3rem' : '2.3rem';
        }

        if (deltaState.selectedName !== undefined) {
            this.inputElement.value = deltaState.selectedName;
        }

        if (deltaState.is_sensitive === true) {
            this.textInputElement.classList.remove(
                'reflex-text-input-disabled'
            );
        } else {
            this.textInputElement.classList.add('reflex-text-input-disabled');
        }
    }
}
