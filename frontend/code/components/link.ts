import { replaceOnlyChildAndResetCssProperties } from '../componentManagement';
import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';

export type LinkState = ComponentState & {
    child_text?: string | null;
    child_component?: number | string | null;
    targetUrl: string;
    isPage: boolean;
};

export class LinkComponent extends SingleContainer {
    state: Required<LinkState>;

    childAttributeName(): string {
        return 'child_component';
    }

    _createElement(): HTMLElement {
        let containerElement = document.createElement('a');
        containerElement.classList.add('rio-link');

        // Listen for clicks
        //
        // This only needs to handle pages, since regular links will be handled
        // by the browser.
        containerElement.addEventListener(
            'click',
            (event) => {
                if (this.state.isPage) {
                    this.sendMessageToBackend({
                        page: this.state.targetUrl,
                    });

                    event.stopPropagation();
                    event.preventDefault();
                }
            },
            { capture: true }
        );

        return containerElement;
    }

    _updateElement(element: HTMLAnchorElement, deltaState: LinkState): void {
        // Child Text?
        if (
            deltaState.child_text !== undefined &&
            deltaState.child_text !== null
        ) {
            // Clear any existing children
            replaceOnlyChildAndResetCssProperties(element, null);

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
            replaceOnlyChildAndResetCssProperties(element, deltaState.child_component);
            element.classList.remove('rio-text-link');
        }

        // Target URL?
        if (deltaState.targetUrl !== undefined) {
            element.href = deltaState.targetUrl;
        }
    }
}
