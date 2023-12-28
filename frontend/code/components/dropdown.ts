import { ComponentBase, ComponentState } from './componentBase';
import { SCROLL_BAR_SIZE } from '../utils';
import { applyIcon } from '../designApplication';
import {
    updateInputBoxNaturalHeight,
    updateInputBoxNaturalWidth,
} from '../inputBoxTools';
import { LayoutContext } from '../layouting';
import { pixelsPerEm } from '../app';

export type DropdownState = ComponentState & {
    _type_: 'Dropdown-builtin';
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

    createElement(): HTMLElement {
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
            let element = this.element;

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
        let element = this.element;

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

        // In order to guarantee that the popup is on top of all components, it
        // must be added to the `body`. `z-index` alone isn't enough because it
        // only affects the "local stacking context".
        document.body.appendChild(this.popupElement);

        // Reset the filter
        //
        // Make sure to do this after the popup has been added to the DOM, so
        // that the scrollHeight is correct.
        this.inputElement.value = '';
        this._updateOptionEntries();

        // Position & Animate
        let dropdownRect = element.getBoundingClientRect();
        let popupHeight = this.popupElement.scrollHeight;
        let windowHeight = window.innerHeight - 1; // innerHeight is rounded

        this.popupElement.style.removeProperty('top');
        this.popupElement.style.removeProperty('bottom');

        const MARGIN_IF_ENTIRELY_ABOVE = 0.5 * pixelsPerEm;

        // Popup is larger than the window. Give it all the space that's
        // available.
        if (popupHeight >= windowHeight) {
            this.popupElement.style.top = '0';
            this.popupElement.classList.add('rio-dropdown-popup-above');
        }
        // Popup fits below the dropdown
        else if (dropdownRect.bottom + popupHeight <= windowHeight) {
            this.popupElement.style.top = `${dropdownRect.bottom}px`;
            this.popupElement.classList.remove('rio-dropdown-popup-above');
        }
        // Popup fits above the dropdown
        else if (dropdownRect.top - popupHeight >= MARGIN_IF_ENTIRELY_ABOVE) {
            this.popupElement.style.bottom = `${
                windowHeight - dropdownRect.top + MARGIN_IF_ENTIRELY_ABOVE
            }px`;
            this.popupElement.classList.add('rio-dropdown-popup-above');
        }
        // Popup doesn't fit above or below the dropdown. Center it as much
        // as possible
        else {
            let top =
                dropdownRect.top + dropdownRect.height / 2 - popupHeight / 2;
            if (top < 0) {
                top = 0;
            } else if (top + popupHeight > windowHeight) {
                top = windowHeight - popupHeight;
            }

            this.popupElement.style.top = `${top}px`;
            this.popupElement.classList.add('rio-dropdown-popup-above');
        }

        this.popupElement.style.left = dropdownRect.left + 'px';
        this.popupElement.style.width = dropdownRect.width + 'px';

        document.addEventListener('click', this.outsideClickHandler, true);
        document.addEventListener('keydown', this.keyDownHandler, true);
    }

    private hidePopup(): void {
        this.isOpen = false;
        this.inputElement.value = this.state.selectedName;

        // Unregister any event handlers
        document.removeEventListener('click', this.outsideClickHandler, true);
        document.removeEventListener('keydown', this.keyDownHandler, true);

        // Animate the disappearance
        this.popupElement.style.height = '0';

        // Remove the element once the animation is done
        setTimeout(() => {
            if (!this.isOpen) {
                this.popupElement.remove();
            }
        }, 300);
    }

    onDestruction(): void {
        super.onDestruction();

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
        let element = this.element;
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

            // The icon is loaded asynchronously, so make sure to give the
            // element some space
            this.popupElement.style.height = '7rem';
        } else {
            // Resize the popup to fit the new content
            this.popupElement.style.height = `${this.optionsElement.scrollHeight}px`;
        }

        // Because the popup isn't a child element of the dropdown, manually
        // make the popup wide enough to fit the widest option + a potential
        // scrollbar.
        element.style.minWidth =
            this.optionsElement.scrollWidth + SCROLL_BAR_SIZE + 'px';
    }

    updateElement(
        deltaState: DropdownState,
        latentComponents: Set<ComponentBase>
    ): void {
        let element = this.element;

        if (deltaState.optionNames !== undefined) {
            this.state.optionNames = deltaState.optionNames;

            if (this.isOpen) {
                this._updateOptionEntries();
            }
        }

        if (deltaState.label !== undefined) {
            let labelElement = element.querySelector(
                '.rio-input-box-label'
            ) as HTMLElement;
            labelElement.textContent = deltaState.label;

            // Update the layout
            updateInputBoxNaturalHeight(this, deltaState.label, 0);
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

    updateNaturalWidth(ctx: LayoutContext): void {
        updateInputBoxNaturalWidth(this, 0);
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        // This is set during the updateElement() call, so there is nothing to
        // do here.
    }
}
