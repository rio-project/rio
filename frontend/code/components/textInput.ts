import { ComponentBase, ComponentState } from './componentBase';
import { getTextDimensions } from '../layoutHelpers';
import { LayoutContext } from '../layouting';
import {
    updateInputBoxNaturalHeight,
    updateInputBoxNaturalWidth,
} from '../inputBoxTools';

export type TextInputState = ComponentState & {
    _type_: 'TextInput-builtin';
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

    private prefixTextWidth: number = 0;
    private suffixTextWidth: number = 0;

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
                this.state.text = this.inputElement.value;
                this.sendMessageToBackend({
                    text: this.state.text,
                });
            }
        });

        // Detect clicks on any part of the component and focus the input
        element.addEventListener('click', () => {
            this.inputElement.focus();
        });

        return element;
    }

    updateElement(
        deltaState: TextInputState,
        latentComponents: Set<ComponentBase>
    ): void {
        if (deltaState.text !== undefined) {
            this.inputElement.value = deltaState.text;
        }

        if (deltaState.label !== undefined) {
            let labelElement = this.element.querySelector(
                '.rio-input-box-label'
            ) as HTMLElement;
            labelElement.textContent = deltaState.label;

            // Update the layout
            updateInputBoxNaturalHeight(
                this,
                deltaState.label === undefined
                    ? this.state.label
                    : deltaState.label,
                0
            );
        }

        if (deltaState.prefix_text !== undefined) {
            let prefixElement = this.element.querySelector(
                '.rio-input-box-prefix-text'
            ) as HTMLElement;
            prefixElement.textContent = deltaState.prefix_text;

            // Update the layout, if needed
            this.prefixTextWidth = getTextDimensions(
                deltaState.prefix_text,
                'text'
            )[0];
            this.makeLayoutDirty();
        }

        if (deltaState.suffix_text !== undefined) {
            let suffixElement = this.element.querySelector(
                '.rio-input-box-suffix-text'
            ) as HTMLElement;
            suffixElement.textContent = deltaState.suffix_text;

            // Update the layout, if needed
            this.prefixTextWidth = getTextDimensions(
                deltaState.suffix_text,
                'text'
            )[0];
            this.makeLayoutDirty();
        }

        if (deltaState.is_secret !== undefined) {
            this.inputElement.type = deltaState.is_secret ? 'password' : 'text';
        }

        if (deltaState.is_sensitive === true) {
            this.inputElement.disabled = false;
            this.element.classList.remove('rio-disabled-input');
        } else if (deltaState.is_sensitive === false) {
            this.inputElement.disabled = true;
            this.element.classList.add('rio-disabled-input');
        }

        if (deltaState.is_valid === false) {
            this.element.style.setProperty(
                '--rio-local-text-color',
                'var(--rio-global-danger-bg)'
            );
        } else if (deltaState.is_valid === true) {
            this.element.style.removeProperty('--rio-local-text-color');
        }
    }

    grabKeyboardFocus(): void {
        this.inputElement.focus();
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        updateInputBoxNaturalWidth(
            this,
            this.prefixTextWidth + this.suffixTextWidth
        );
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        // This is set during the updateElement() call, so there is nothing to
        // do here.
    }
}
