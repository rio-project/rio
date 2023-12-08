import { ComponentBase, ComponentState } from './componentBase';
import { SCROLL_BAR_SIZE } from '../utils';
import { applyIcon } from '../designApplication';

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
    private inputElement: HTMLInputElement;

    private isOpen: boolean = false;

    // Event handlers, already bound to `this`, so they can be disconnected
    private outsideClickHandler: (event: MouseEvent) => void;
    private keyDownHandler: (event: KeyboardEvent) => void;

    // The currently highlighted option, if any
    private highlightedOptionName: HTMLElement | null = null;

    _createElement(): HTMLElement {
        // Create the elements
        let element = document.createElement('div');
        element.classList.add(
            'rio-dropdown',
            'mdc-ripple-surface',
            'rio-input-box'
        );

        element.innerHTML = `
            <input type="text" placeholder="" style="pointer-events: none" disabled>
            <div class="rio-input-box-label"></div>
            <div class="rio-dropdown-arrow"></div>
            <div class="rio-input-box-plain-bar"></div>
            <div class="rio-input-box-color-bar"></div>
        `;

        // Expose them as properties
        this.inputElement = element.querySelector('input') as HTMLInputElement;

        this.popupElement = document.createElement('div');
        this.popupElement.classList.add('rio-dropdown-popup');

        this.optionsElement = document.createElement('div');
        this.optionsElement.classList.add('rio-dropdown-options');
        this.popupElement.appendChild(this.optionsElement);

        // Add an arrow icon
        let arrowElement = element.querySelector(
            '.rio-dropdown-arrow'
        ) as HTMLElement;
        applyIcon(arrowElement, 'expand-more', 'var(--rio-local-text-color)');

        // Connect events
        element.addEventListener('click', () => {
            let element = this.element();

            // Already open?
            if (this.isOpen) {
                // Hide it
                this.hidePopup();

                // Make the text input appear as inactive
                element.classList.remove('rio-input-box-focused');
                return;
            }

            // Show the popup
            this.showPopup(element);

            // Make the text input appear as active
            element.classList.add('rio-input-box-focused');
        });

        // Bind events so they can be connected/disconnected at will
        this.outsideClickHandler = this._outsideClickHandler.bind(this);
        this.keyDownHandler = this._keydownHandler.bind(this);

        return element;
    }

    _outsideClickHandler(event: MouseEvent): void {
        let element = this.element();

        // Clicks into the dropdown are handled elsewhere
        if (
            event.target === element ||
            element.contains(event.target as Node)
        ) {
            return;
        }

        // Make the text input appear as inactive
        element.classList.remove('rio-input-box-focused');

        // Hide the popup
        this.hidePopup();
    }

    _keydownHandler(event: KeyboardEvent): void {
        // Close the dropdown on escape
        if (event.key === 'Escape') {
            this.hidePopup();
        }

        // Backspace -> remove the last character from the filter text
        else if (event.key === 'Backspace') {
            this.inputElement.value = this.inputElement.value.slice(0, -1);
            this._updateOptionEntries();
        }

        // Enter -> select the highlighted option
        else if (event.key === 'Enter') {
            if (this.highlightedOptionName !== null) {
                this.highlightedOptionName.click();
            }
        }
        // Move highlight up
        else if (event.key === 'ArrowDown') {
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
        // Move highlight down
        else if (event.key === 'ArrowUp') {
            let nextOption;

            if (this.highlightedOptionName === null) {
                nextOption = this.optionsElement.lastElementChild;
            } else {
                nextOption = this.highlightedOptionName.previousElementSibling;

                if (nextOption === null) {
                    nextOption = this.optionsElement.lastElementChild;
                }
            }

            this._highlightOption(nextOption as HTMLElement);
        }
        // Any other key -> add it to the filter text
        else if (event.key.length === 1) {
            this.inputElement.value += event.key.toLowerCase();
            this._updateOptionEntries();
        } else {
            return;
        }

        event.stopPropagation();
        event.preventDefault();
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
        this.isOpen = true;

        // Reset the filter
        this.inputElement.value = '';
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

        document.addEventListener('click', this.outsideClickHandler, true);
        document.addEventListener('keydown', this.keyDownHandler, true);
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

    private hidePopup(): void {
        this.isOpen = false;
        this.popupElement.remove();
        this.popupElement.style.removeProperty('width');
        this.inputElement.value = this.state.selectedName;

        // Unregister any event handlers
        document.removeEventListener('click', this.outsideClickHandler, true);
        document.removeEventListener('keydown', this.keyDownHandler, true);
    }

    onDestruction(): void {
        this.popupElement.remove();
    }

    /// Find needle in haystack, returning a HTMLElement with the matched
    /// sections highlighted. If no match is found, return null. Needle must be
    /// lowercase.
    _highlightMatches(
        haystack: string,
        needleLower: string
    ): HTMLElement | null {
        // Special case: Empty needle matches everything, and would cause a hang
        // in the while loop below
        if (needleLower.length === 0) {
            const container = document.createElement('div');
            container.textContent = haystack;
            return container;
        }

        // Create a div element to hold the highlighted content
        const container = document.createElement('div');

        // Start searching
        let startIndex = 0;
        let haystackLower = haystack.toLowerCase();
        let index = haystackLower.indexOf(needleLower, startIndex);

        while (index !== -1) {
            // Add the text before the match as a text node
            container.appendChild(
                document.createTextNode(haystack.substring(startIndex, index))
            );

            // Add the matched portion as a highlighted span
            const span = document.createElement('span');
            span.className = 'rio-dropdown-option-highlight';
            span.textContent = haystack.substring(
                index,
                index + needleLower.length
            );
            container.appendChild(span);

            // Update the start index for the next search
            startIndex = index + needleLower.length;

            // Find the next occurrence of needle in haystack
            index = haystackLower.indexOf(needleLower, startIndex);
        }

        // Add any remaining text after the last match
        container.appendChild(
            document.createTextNode(haystack.substring(startIndex))
        );

        // Was anything found?
        return container.children.length === 0 ? null : container;
    }

    /// Update the visible options based on everything matching the search
    /// filter
    _updateOptionEntries() {
        let element = this.element();
        this.optionsElement.innerHTML = '';
        let needleLower = this.inputElement.value.toLowerCase();

        // Find matching options
        for (let optionName of this.state.optionNames) {
            let match = this._highlightMatches(optionName, needleLower);

            if (match === null) {
                continue;
            }

            match.classList.add('rio-dropdown-option');
            this.optionsElement.appendChild(match);

            match.addEventListener('click', () => {
                this.state.selectedName = optionName;
                this.hidePopup();
                this.sendMessageToBackend({
                    name: optionName,
                });
            });

            match.addEventListener('mouseenter', () => {
                this._highlightOption(match);
            });
        }

        // If only one option was found, highlight it
        if (this.optionsElement.children.length === 1) {
            this._highlightOption(
                this.optionsElement.firstElementChild as HTMLElement
            );
        }

        // Was anything found?
        if (this.optionsElement.children.length === 0) {
            applyIcon(
                this.optionsElement,
                'error',
                'var(--rio-local-text-color)'
            );
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
                '.rio-input-box-label'
            ) as HTMLElement;
            labelElement.textContent = deltaState.label;

            if (deltaState.label.length > 0) {
                element.classList.add('rio-input-box-with-label');
            } else {
                element.classList.remove('rio-input-box-with-label');
            }
        }

        if (deltaState.selectedName !== undefined) {
            this.inputElement.value = deltaState.selectedName;
        }

        if (deltaState.is_sensitive === true) {
            element.classList.remove('rio-input-box-disabled');
        } else if (deltaState.is_sensitive === false) {
            element.classList.add('rio-input-box-disabled');
        }
    }
}
