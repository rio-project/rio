import { sendEventOverWebsocket } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type SwitchJson = WidgetState & {
    _type_: 'switch';
    is_on?: boolean;
};

export class SwitchWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-switch');

        element.addEventListener('click', () => {
            sendEventOverWebsocket(element, 'switchChangeEvent', {
                isOn: element.textContent !== 'true',
            });
        });

        return element;
    }

    updateElement(element: HTMLElement, deltaState: SwitchJson): void {
        if (deltaState.is_on !== undefined) {
            element.textContent = deltaState.is_on.toString();
            element.style.backgroundColor = deltaState.is_on ? 'green' : 'red';
        }
    }
}
