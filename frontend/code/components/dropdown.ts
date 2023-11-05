import { ComponentBase, ComponentState } from './componentBase';

export type DropdownState = ComponentState & {
    _type_: 'dropdown';
    optionNames?: string[];
    label?: string;
    selectedName?: string;
    is_sensitive?: boolean;
};

function showPopup(parent: HTMLElement, popup: HTMLElement): void {
    document.body.appendChild(popup);

    let clientRect = parent.getBoundingClientRect();

    popup.style.left = clientRect.left + 'px';
    popup.style.top = clientRect.bottom + 'px';
    popup.style.width = clientRect.width + 'px';
    popup.style.maxHeight = popup.scrollHeight + 'px';
}

function hidePopup(parent: HTMLElement, popup: HTMLElement): void {
    popup.remove();

    popup.style.maxHeight = '0px';
}

export class DropdownComponent extends ComponentBase {
    state: Required<DropdownState>;

    private popupElement: HTMLElement;
    private optionsElement: HTMLElement;
    private textInputElement: HTMLElement;
    private inputElement: HTMLInputElement;

    private isOpen: boolean = false;

    _createElement(): HTMLElement {
        // Create the elements
        let element = document.createElement('div');
        element.classList.add('rio-dropdown');
        element.classList.add('mdc-ripple-surface');

        element.innerHTML = `
        <div class="rio-text-input">
            <input type="text" placeholder="" style="pointer-events: none" disabled>
            <div class="rio-text-input-label"></div>
            <div class="rio-icon-revealer-arrow"></div>
            <div class="rio-text-input-plain-bar"></div>
            <div class="rio-text-input-color-bar"></div>
        </div>
        `;

        // Expose them as properties
        this.textInputElement = element.querySelector(
            '.rio-text-input'
        ) as HTMLElement;

        this.inputElement = element.querySelector('input') as HTMLInputElement;

        this.popupElement = document.createElement('div');
        this.popupElement.classList.add('rio-dropdown-popup');

        this.optionsElement = document.createElement('div');
        this.optionsElement.classList.add('rio-dropdown-options');
        this.popupElement.appendChild(this.optionsElement);

        // Connect events
        let outsideClickListener = (event) => {
            // Clicks into the dropdown are handled elsewhere
            if (event.target === element || element.contains(event.target)) {
                return;
            }

            // Hide the popup
            hidePopup(element, this.popupElement);
            this.isOpen = false;

            // Unregister the event listener
            document.removeEventListener('click', outsideClickListener);
        };

        this.textInputElement.addEventListener('click', () => {
            // Hide if open
            if (this.isOpen) {
                hidePopup(element, this.popupElement);
                this.isOpen = false;
                return;
            }

            // Show the popup
            showPopup(element, this.popupElement);
            this.isOpen = true;
            document.addEventListener('click', outsideClickListener);
        });

        return element;
    }

    _updateElement(element: HTMLElement, deltaState: DropdownState): void {
        if (deltaState.optionNames !== undefined) {
            this.optionsElement.innerHTML = '';

            for (let optionName of deltaState.optionNames) {
                let optionElement = document.createElement('div');
                optionElement.classList.add('rio-dropdown-option');
                optionElement.textContent = optionName;
                this.optionsElement.appendChild(optionElement);

                optionElement.addEventListener('click', () => {
                    hidePopup(element, this.popupElement);
                    this.isOpen = false;
                    this.inputElement.value = optionName;
                    this.sendMessageToBackend({
                        name: optionName,
                    });
                });
            }
        }

        if (deltaState.label !== undefined) {
            let labelElement = element.querySelector(
                '.rio-text-input-label'
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
            this.textInputElement.classList.remove('rio-text-input-disabled');
        } else {
            this.textInputElement.classList.add('rio-text-input-disabled');
        }
    }
}
