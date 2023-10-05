import { replaceOnlyChild } from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type LinkState = ComponentState & {
    child_text?: string | null;
    child_component?: number | string | null;
    targetUrl: string;
    isRoute: boolean;
};

export class LinkComponent extends ComponentBase {
    state: Required<LinkState>;

    createElement(): HTMLElement {
        let containerElement = document.createElement('a');
        containerElement.classList.add('rio-link');
        containerElement.classList.add('rio-single-container');

        // Listen for clicks
        //
        // This only needs to handle routes, since regular links will be handled
        // by the browser.
        containerElement.addEventListener(
            'click',
            (event) => {
                if (this.state.isRoute) {
                    this.sendMessageToBackend({
                        route: this.state.targetUrl,
                    });

                    event.stopPropagation();
                    event.preventDefault();
                }
            },
            { capture: true }
        );

        return containerElement;
    }

    updateElement(element: HTMLAnchorElement, deltaState: LinkState): void {
        // Child Text?
        if (
            deltaState.child_text !== undefined &&
            deltaState.child_text !== null
        ) {
            // Clear any existing children
            replaceOnlyChild(element, null);

            // Add the new text
            let textElement = document.createElement('div');
            element.appendChild(textElement);
            textElement.innerText = deltaState.child_text;

            // Update the CSS classes
            element.classList.add('rio-text-link');
        }

        // Child Component?
        if (
            deltaState.child_component !== undefined &&
            deltaState.child_component !== null
        ) {
            replaceOnlyChild(element, deltaState.child_component);
            element.classList.remove('rio-text-link');
        }

        // Target URL?
        if (deltaState.targetUrl !== undefined) {
            element.href = deltaState.targetUrl;
        }
    }
}
