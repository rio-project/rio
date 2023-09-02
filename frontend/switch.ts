import { WidgetBase, WidgetState } from './widgetBase';
import { MDCSwitch } from '@material/switch';

export type SwitchState = WidgetState & {
    _type_: 'switch';
    is_on?: boolean;
    is_sensitive?: boolean;
};

export class SwitchWidget extends WidgetBase {
    private mdcSwitch: MDCSwitch;

    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('button');
        element.classList.add('mdc-switch');
        element.classList.add('mdc-switch--unselected');
        element.setAttribute('type', 'button');
        element.setAttribute('role', 'switch');
        element.setAttribute('aria-checked', 'false');

        element.innerHTML = `
<div class="mdc-switch__track"></div>
<div class="mdc-switch__handle-track">
    <div class="mdc-switch__handle">
        <div class="mdc-switch__shadow">
            <div class="mdc-elevation-overlay"></div>
        </div>
        <div class="mdc-switch__ripple"></div>
    </div>
</div>
`;
        // Initialize the material design component
        this.mdcSwitch = new MDCSwitch(element);

        // Detect value changes and send them to the backend
        element.addEventListener('click', () => {
            this.setStateAndNotifyBackend({
                is_on: this.mdcSwitch.selected,
            });
        });

        // this.setStateAndNotifyBackend({
        //     is_on: this.mdcSwitch.selected,
        // });

        return element;
    }

    updateElement(element: HTMLElement, deltaState: SwitchState): void {
        if (deltaState.is_on !== undefined) {
            this.mdcSwitch.selected = deltaState.is_on;
        }

        if (deltaState.is_sensitive !== undefined) {
            this.mdcSwitch.disabled = !deltaState.is_sensitive;
        }
    }
}
