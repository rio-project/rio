import { ComponentBase, ComponentState } from './componentBase';

// TODO
export type HtmlState = ComponentState & {
    _type_: 'Html-builtin';
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
