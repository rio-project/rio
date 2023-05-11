import { JsonButton } from "./models";
import { sendEvent } from "./app";

export class ButtonWidget {
    static build(data: JsonButton): HTMLElement {
        let element = document.createElement('button');
        element.type = 'button';

        element.addEventListener('click', () => {
            sendEvent(element, 'buttonPressedEvent', {});
        });

        return element;
    }

    static update(element: HTMLElement, deltaState: JsonButton): void {
        if (deltaState.text !== undefined) {
            element.textContent = deltaState.text;
        }
    }
}