import { componentsById } from '../componentManagement';
import { getTextDimensions } from '../layoutHelpers';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';

export type LinkState = ComponentState & {
    _type_: 'Link-builtin';
    child_text?: string | null;
    child_component?: ComponentId | null;
    open_in_new_tab?: boolean;
    targetUrl: string;
    isPage: boolean;
};

export class LinkComponent extends ComponentBase {
    state: Required<LinkState>;

    childAttributeName(): string {
        return 'child_component';
    }

    createElement(): HTMLElement {
        let containerElement = document.createElement('a');
        containerElement.classList.add('rio-link');

        // Listen for clicks
        //
        // This only needs to handle pages, since regular links will be handled
        // by the browser.
        containerElement.addEventListener('click', (event: MouseEvent) => {
            if (this.state.isPage) {
                this.sendMessageToBackend({
                    page: this.state.targetUrl,
                });
            } else if (globalThis.RUNNING_IN_WINDOW) {
                this.sendMessageToBackend({
                    open: this.state.targetUrl,
                });
            } else {
                return;
            }

            event.stopPropagation();
            event.preventDefault();
        });

        return containerElement;
    }

    updateElement(
        deltaState: LinkState,
        latentComponents: Set<ComponentBase>
    ): void {
        let element = this.element as HTMLAnchorElement;

        // Child Text?
        if (
            deltaState.child_text !== undefined &&
            deltaState.child_text !== null
        ) {
            // Clear any existing children
            this.replaceFirstChild(latentComponents, null);

            // Add the new text
            let textElement = document.createElement('div');
            element.appendChild(textElement);
            textElement.textContent = deltaState.child_text;

            // Update the CSS classes
            element.classList.add('rio-text-link');
        }

        // Child Component?
        if (
            deltaState.child_component !== undefined &&
            deltaState.child_component !== null
        ) {
            this.replaceFirstChild(
                latentComponents,
                deltaState.child_component
            );
            element.classList.remove('rio-text-link');
        }

        // Target URL?
        if (deltaState.targetUrl !== undefined) {
            element.href = deltaState.targetUrl;
        }

        // Open in new tab?
        if (deltaState.open_in_new_tab === true) {
            element.target = '_blank';
        } else if (deltaState.open_in_new_tab === false) {
            element.target = '';
        }
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        if (this.state.child_component === null) {
            [this.naturalWidth, this.naturalHeight] = getTextDimensions(
                this.state.child_text!,
                'text'
            );
        } else {
            this.naturalWidth =
                componentsById[this.state.child_component]!.requestedWidth;
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        if (this.state.child_component !== null) {
            componentsById[this.state.child_component]!.allocatedWidth =
                this.allocatedWidth;
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        if (this.state.child_component === null) {
            // Already set in updateRequestedWidth
        } else {
            this.naturalHeight =
                componentsById[this.state.child_component]!.requestedHeight;
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        if (this.state.child_component !== null) {
            componentsById[this.state.child_component]!.allocatedHeight =
                this.allocatedHeight;

            let element = componentsById[this.state.child_component]!.element;
            element.style.left = '0';
            element.style.top = '0';
        }
    }
}
