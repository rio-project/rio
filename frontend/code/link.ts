import { replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type LinkState = WidgetState & {
    child_text?: string | null;
    child_widget?: number | string | null;
    targetUrl: string;
    isRoute: boolean;
};

export class LinkWidget extends WidgetBase {
    state: Required<LinkState>;

    createElement(): HTMLElement {
        let containerElement = document.createElement('div');
        containerElement.classList.add('rio-link');

        // Listen for clicks
        //
        // This only needs to handle routes, since regular links will be handled
        // by the browser.
        containerElement.addEventListener('click', (event) => {
            if (this.state.isRoute) {
                this.sendMessageToBackend({
                    route: this.state.targetUrl,
                });
            }
        });

        return containerElement;
    }

    updateElement(containerElement: HTMLElement, deltaState: LinkState): void {
        // Child Text?
        if (
            deltaState.child_text !== undefined &&
            deltaState.child_text !== null
        ) {
            // Clear any existing children
            replaceOnlyChild(containerElement, null);

            // Add a link element
            let linkElement = document.createElement('a');

            if (!deltaState.isRoute) {
                linkElement.href = deltaState.targetUrl;
            }

            linkElement.innerText = deltaState.child_text;
            containerElement.appendChild(linkElement);

            // Update the CSS classes
            containerElement.classList.add('rio-text-link');
            containerElement.classList.remove('rio-single-container');
        }

        // Child Widget?
        if (
            deltaState.child_widget !== undefined &&
            deltaState.child_widget !== null
        ) {
            replaceOnlyChild(containerElement, deltaState.child_widget);
            containerElement.classList.add('rio-single-container');
            containerElement.classList.remove('rio-text-link');
        }
    }
}
