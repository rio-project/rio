import { ComponentBase, ComponentState } from './componentBase';

export type HtmlState = ComponentState & {
    html?: string;
};

export class HtmlComponent extends ComponentBase {
    state: Required<HtmlState>;

    createElement(): HTMLElement {
        return document.createElement('div');
    }

    updateElement(element: HTMLAnchorElement, deltaState: HtmlState): void {
        if (deltaState.html !== undefined) {
            element.innerHTML = deltaState.html;
        }
    }
}
