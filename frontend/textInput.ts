import { JsonMouseEventListener, JsonTextInput } from './models';
import { buildWidget, pixelsPerEm, sendEvent } from './app';

export class TextInputWidget {
    static build(data: JsonTextInput): HTMLElement {
        let element = document.createElement('input');
        element.classList.add('reflex-text-input');

        element.addEventListener('blur', () => {
            sendEvent(element, 'textInputBlurEvent', {
                text: element.value,
            });
        });

        return element;
    }

    static update(element: HTMLElement, deltaState: JsonTextInput): void {
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
