import { replaceOnlyChild } from '../widgetManagement';
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

        // Child Widget?
        if (
            deltaState.child_widget !== undefined &&
            deltaState.child_widget !== null
        ) {
            replaceOnlyChild(element, deltaState.child_widget);
            element.classList.remove('rio-text-link');
        }

        // Target URL?
        if (deltaState.targetUrl !== undefined) {
            element.href = deltaState.targetUrl;
        }
    }
}
