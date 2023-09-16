import { replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type LinkState = WidgetState & {
    child_text?: string | null;
    child_widget?: number | string | null;
    link: string;
    is_route: boolean;
};

export class LinkWidget extends WidgetBase {
    state: Required<LinkState>;

    createElement(): HTMLElement {
        let containerElement = document.createElement('div');
        containerElement.classList.add('reflex-link');

        // Listen for clicks
        //
        // This only needs to handle routes, since regular links will be handled
        // by the browser.
        containerElement.addEventListener('click', (event) => {
            if (this.state.is_route) {
                this.sendMessageToBackend({
                    route: this.state.link,
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

            if (!deltaState.is_route) {
                linkElement.href = deltaState.link;
            }

            linkElement.innerText = deltaState.child_text;
            containerElement.appendChild(linkElement);

            // Update the CSS classes
            containerElement.classList.add('reflex-text-link');
            containerElement.classList.remove('reflex-single-container');
        }

        // Child Widget?
        if (
            deltaState.child_widget !== undefined &&
            deltaState.child_widget !== null
        ) {
            replaceOnlyChild(containerElement, deltaState.child_widget);
            containerElement.classList.add('reflex-single-container');
            containerElement.classList.remove('reflex-text-link');
        }
    }
}
