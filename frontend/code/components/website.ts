import { ComponentBase, ComponentState } from './componentBase';
// TODO

export type WebsiteState = ComponentState & {
    _type_: 'Website-builtin';
    url?: string;
};

export class WebsiteComponent extends ComponentBase {
    state: Required<WebsiteState>;

    createElement(): HTMLElement {
        return document.createElement('iframe');
    }

    updateElement(element: HTMLIFrameElement, deltaState: WebsiteState): void {
        if (deltaState.url !== undefined && deltaState.url !== element.src) {
            element.src = deltaState.url;
        }
    }
}
