import { ComponentBase, ComponentState } from './componentBase';
import { SCROLL_BAR_SIZE } from '../utils';

export type DropdownState = ComponentState & {
    _type_: 'dropdown';
    optionNames?: string[];
    label?: string;
    selectedName?: string;
    is_sensitive?: boolean;
};

export class DropdownComponent extends ComponentBase {
    state: Required<DropdownState>;

    private popupElement: HTMLElement;
    private optionsElement: HTMLElement;
    private textInputElement: HTMLElement;
    private inputElement: HTMLInputElement;

    private isOpen: boolean = false;

    // If the user types while the dropdown is open, this text is used to filter
    // available options.
    private filterText: string = '';

    //The currently highlighted option, if any
    private highlightedOptionName: HTMLElement | null = null;

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
            this.hidePopup(element);
            this.isOpen = false;

            // Unregister the event listener
            document.removeEventListener('click', outsideClickListener);
        };

        this.textInputElement.addEventListener('click', () => {
            // Hide if open
            if (this.isOpen) {
                this.hidePopup(element);
                this.isOpen = false;
                return;
            }

            // Show the popup
            this.showPopup(element);
            this.isOpen = true;
            document.addEventListener('click', outsideClickListener);
        });

        return element;
    }

    private _highlightOption(optionElement: HTMLElement | null): void {
        // Remove the highlight from the previous option
        if (this.highlightedOptionName !== null) {
            this.highlightedOptionName.classList.remove(
                'rio-dropdown-option-highlighted'
            );
        }

        // Remember the new option and highlight it
        this.highlightedOptionName = optionElement;

        if (optionElement !== null) {
            optionElement.classList.add('rio-dropdown-option-highlighted');
        }
    }

    private showPopup(element: HTMLElement): void {
        // Reset the filter
        this.filterText = '';
        this._updateOptionEntries();

        // In order to guarantee that the popup is on top of all components, it
        // must be added to the `body`. `z-index` alone isn't enough because it
        // only affects the "local stacking context".
        document.body.appendChild(this.popupElement);

        let clientRect = element.getBoundingClientRect();
        let popupHeight = this.popupElement.scrollHeight;
        let windowHeight = window.innerHeight;

        if (popupHeight >= windowHeight) {
            // Popup is larger than the window. Give it all the space that's
            // available.
            this.animatePopupDownwards(0, windowHeight);
        } else if (clientRect.bottom + popupHeight <= windowHeight) {
            // Popup fits below the dropdown
            this.animatePopupDownwards(clientRect.bottom, popupHeight);
        } else if (clientRect.top - popupHeight >= 0) {
            // Popup fits above the dropdown
            this.popupElement.style.top = clientRect.top - popupHeight + 'px';
            this.popupElement.style.maxHeight = popupHeight + 'px';
            this.animatePopupUpwards(clientRect.top - popupHeight, popupHeight);
        } else {
            // Popup doesn't fit above or below the dropdown. Center it as much
            // as possible
            let top = clientRect.top + clientRect.height / 2 - popupHeight / 2;
            if (top < 0) {
                top = 0;
            } else if (top + popupHeight > windowHeight) {
                top = windowHeight - popupHeight;
            }

            this.animatePopupDownwards(top, popupHeight);
        }

        this.popupElement.style.left = clientRect.left + 'px';
        this.popupElement.style.width = clientRect.width + 'px';

        // Listen for key presses
        let keyDownListener = (event) => {
            // Do nothing and disconnect if the dropdown is closed
            if (!this.isOpen) {
                document.removeEventListener('keydown', keyDownListener);
                return;
            }

            // Close the dropdown on escape
            if (event.key === 'Escape') {
                this.hidePopup(element);
                this.isOpen = false;
                document.removeEventListener('keydown', keyDownListener);
                return;
            }

            // Backspace -> remove the last character from the filter text
            if (event.key === 'Backspace') {
                this.filterText = this.filterText.slice(0, -1);
                this._updateOptionEntries();
            }

            // Enter -> select the highlighted option
            if (event.key === 'Enter') {
                if (this.highlightedOptionName !== null) {
                    this.highlightedOptionName.click();
                }
            }

            // Arrow keys -> move the highlight
            if (event.key === 'ArrowDown') {
                let nextOption;

                if (this.highlightedOptionName === null) {
                    nextOption = this.optionsElement.firstElementChild;
                } else {
                    nextOption = this.highlightedOptionName.nextElementSibling;

                    if (nextOption === null) {
                        nextOption = this.optionsElement.firstElementChild;
                    }
                }

                this._highlightOption(nextOption as HTMLElement);
            }

            if (event.key === 'ArrowUp') {
                let nextOption;

                if (this.highlightedOptionName === null) {
                    nextOption = this.optionsElement.lastElementChild;
                } else {
                    nextOption =
                        this.highlightedOptionName.previousElementSibling;

                    if (nextOption === null) {
                        nextOption = this.optionsElement.lastElementChild;
                    }
                }

                this._highlightOption(nextOption as HTMLElement);
            }

            // Any other key -> add it to the filter text
            if (event.key.length === 1) {
                this.filterText += event.key;
                this._updateOptionEntries();
            }
        };

        document.addEventListener('keydown', keyDownListener);
    }

    private animatePopupDownwards(top: number, height: number): void {
        let keyframes = [
            {
                top: top + 'px',
                height: '0px',
            },
            {
                top: top + 'px',
                height: height + 'px',
            },
        ];
        this.animatePopup(keyframes);
    }

    private animatePopupUpwards(top: number, height: number): void {
        let keyframes = [
            {
                top: top + height + 'px',
                height: '0px',
            },
            {
                top: top + 'px',
                height: height + 'px',
            },
        ];
        this.animatePopup(keyframes);
    }

    private animatePopup(keyframes: Keyframe[]): void {
        this.popupElement.style.top = keyframes[0].top as string;
        this.popupElement.style.height = keyframes[0].height as string;
        this.popupElement.style.overflowY = 'hidden';

        let animation = this.popupElement.animate(keyframes, {
            duration: 140,
            easing: 'ease-in-out',
            fill: 'both',
        });

        animation.onfinish = () => {
            this.popupElement.style.overflowY = 'auto';
        };
    }

    private hidePopup(element: HTMLElement): void {
        this.popupElement.remove();
        this.popupElement.style.removeProperty('width');
    }

    onDestruction(): void {
        this.popupElement.remove();
    }

    _updateOptionEntries() {
        let element = this.element();

        // Find all options which should currently be displayed
        let currentOptionNames: string[] = [];

        for (let optionName of this.state.optionNames) {
            if (optionName.toLowerCase().includes(this.filterText)) {
                currentOptionNames.push(optionName);
            }
        }

        // Update the HTML to reflect them
        this.optionsElement.innerHTML = '';
        for (let optionName of currentOptionNames) {
            let optionElement = document.createElement('div');
            optionElement.classList.add('rio-dropdown-option');
            optionElement.textContent = optionName;
            this.optionsElement.appendChild(optionElement);

            optionElement.addEventListener('click', () => {
                this.hidePopup(element);
                this.isOpen = false;
                this.inputElement.value = optionName;
                this.sendMessageToBackend({
                    name: optionName,
                });
            });

            optionElement.addEventListener('mouseenter', () => {
                this._highlightOption(optionElement);
            });
        }

        // Because the popup isn't a child element of the dropdown, manually
        // make the popup wide enough to fit the widest option + a potential
        // scrollbar.
        element.style.minWidth =
            this.optionsElement.scrollWidth + SCROLL_BAR_SIZE + 'px';
    }

    _updateElement(element: HTMLElement, deltaState: DropdownState): void {
        if (deltaState.optionNames !== undefined) {
            this.state.optionNames = deltaState.optionNames;
            this._updateOptionEntries();
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