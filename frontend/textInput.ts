import { WidgetBase, WidgetState } from './widgetBase';

export type TextInputState = WidgetState & {
    _type_: 'textInput';
    text?: string;
    placeholder?: string;
    secret?: boolean;
};

export class TextInputWidget extends WidgetBase {
    createInnerElement(): HTMLElement {
        let element = document.createElement('input');
        element.classList.add('reflex-text-input');

        // Detect value changes and send them to the backend
        element.addEventListener('blur', () => {
            this.setStateAndNotifyBackend({
                text: element.value,
            });
        });

        // Detect the enter key and send it to the backend
        //
        // In addition to notifying the backend, also include the input's
        // current value. This ensures any event handlers actually use the up-to
        // date value.
        element.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                this.sendMessageToBackend({
                    text: element.value,
                });
            }
        });

        return element;
    }

    updateInnerElement(element: HTMLElement, deltaState: TextInputState): void {
        let cast_element = element as HTMLInputElement;

        if (deltaState.secret !== undefined) {
            cast_element.type = deltaState.secret ? 'password' : 'text';
        }

        if (deltaState.text !== undefined) {
            cast_element.value = deltaState.text;
        }

        if (deltaState.placeholder !== undefined) {
            cast_element.placeholder = deltaState.placeholder;
        }
    }
}
