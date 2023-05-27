import { sendEventOverWebsocket } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type TextInputState = WidgetState & {
    _type_: 'textInput';
    text?: string;
    placeholder?: string;
    secret?: boolean;
};

export class TextInputWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('input');
        element.classList.add('reflex-text-input');

        element.addEventListener('blur', () => {
            sendEventOverWebsocket(element, 'textInputBlurEvent', {
                text: element.value,
            });
        });

        return element;
    }

    updateElement(element: HTMLElement, deltaState: TextInputState): void {
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
