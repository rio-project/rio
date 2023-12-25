import { LayoutContext } from '../layouting';
import { ComponentBase, ComponentState } from './componentBase';

export type DebuggerConnectorState = ComponentState & {
    _type_: 'DebuggerConnector-builtin';
};

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

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth = 3;
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        this.naturalHeight = 7;
    }
}
