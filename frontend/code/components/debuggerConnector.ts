import { LayoutContext } from '../layouting';
import { ComponentBase, ComponentState } from './componentBase';

export type DebuggerConnectorState = ComponentState & {};

export class DebuggerConnectorComponent extends ComponentBase {
    state: Required<DebuggerConnectorState>;

    createElement(): HTMLElement {
        let element = document.createElement('a');
        element.href = 'https://rio.dev';
        element.target = '_blank';
        element.classList.add('rio-debugger-navigation-rio-logo');
        element.innerHTML = `
            <img src="/rio/asset/rio-logo.png">
            <div>Rio</div>
        `;
        return element;
    }

    updateElement(
        element: HTMLElement,
        deltaState: DebuggerConnectorState
    ): void {}

    updateRequestedWidth(ctx: LayoutContext): void {
        this.requestedWidth = 3;
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        this.requestedHeight = 7;
    }
}
