import { ComponentBase, ComponentState } from './componentBase';


export type HtmlState = ComponentState & {
    html?: string;
};


export class HtmlComponent extends ComponentBase {
    state: Required<HtmlState>;

    _createElement(): HTMLElement {
        return document.createElement('div');
    }

    _updateElement(element: HTMLAnchorElement, deltaState: HtmlState): void {
        if (deltaState.html !== undefined) {
            element.innerHTML = deltaState.html;
        }
    }
}
