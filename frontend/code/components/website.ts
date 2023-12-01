import { ComponentBase, ComponentState } from './componentBase';

export type WebsiteState = ComponentState & {
    url?: string;
};

export class WebsiteComponent extends ComponentBase {
    state: Required<WebsiteState>;

    _createElement(): HTMLElement {
        return document.createElement('iframe');
    }

    _updateElement(element: HTMLIFrameElement, deltaState: WebsiteState): void {
        if (deltaState.url !== undefined && deltaState.url !== element.src) {
            element.src = deltaState.url;
        }
    }
}
