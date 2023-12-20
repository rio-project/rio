import { replaceOnlyChild } from '../componentManagement';
import { getTextDimensions } from '../layoutHelpers';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';

export type LinkState = ComponentState & {
    child_text?: string | null;
    child_component?: ComponentId | null;
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
        containerElement.addEventListener(
            'click',
            (event: MouseEvent) => {
                if (this.state.isPage) {
                    this.sendMessageToBackend({
                        page: this.state.targetUrl,
                    });

                    event.stopPropagation();
                    event.preventDefault();
                } else {
                    // Delete the connection-lost-popup, otherwise it would
                    // become visible for a little while
                    let connectionLostPopup = document.querySelector(
                        '.rio-connection-lost-popup'
                    ) as HTMLElement;
                    connectionLostPopup.remove();
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
            replaceOnlyChild(element.id, element, null);

            // Add the new text
            let textElement = document.createElement('div');
            element.appendChild(textElement);
            textElement.textContent = deltaState.child_text;

            // Update the CSS classes
            element.classList.add('rio-text-link');

            // Update the layout
            this.makeLayoutDirty();
        }

        // Child Component?
        if (
            deltaState.child_component !== undefined &&
            deltaState.child_component !== null
        ) {
            replaceOnlyChild(element.id, element, deltaState.child_component);
            element.classList.remove('rio-text-link');
            this.makeLayoutDirty();
        }

        // Target URL?
        if (deltaState.targetUrl !== undefined) {
            element.href = deltaState.targetUrl;
        }
    }

    updateRequestedWidth(ctx: LayoutContext): void {
        if (this.state.child_component === null) {
            [this.requestedWidth, this.requestedHeight] = getTextDimensions(
                this.state.child_text!,
                'text'
            );
        } else {
            this.requestedWidth = ctx.inst(
                this.state.child_component
            ).requestedWidth;
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        if (this.state.child_component !== null) {
            ctx.inst(this.state.child_component).allocatedWidth =
                this.allocatedWidth;
        }
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        if (this.state.child_component === null) {
            // Already set in updateRequestedWidth
        } else {
            this.requestedHeight = ctx.inst(
                this.state.child_component
            ).requestedHeight;
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        if (this.state.child_component !== null) {
            ctx.inst(this.state.child_component).allocatedHeight =
                this.allocatedHeight;

            let element = ctx.elem(this.state.child_component);
            element.style.left = '0';
            element.style.top = '0';
        }
    }
}
