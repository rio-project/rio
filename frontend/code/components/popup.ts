import { pixelsPerEm } from '../app';
import { replaceOnlyChild } from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';
// TODO

export type PopupState = ComponentState & {
    _type_: 'Popup-builtin';
    anchor?: number | string;
    content?: number | string;
    direction?: 'left' | 'top' | 'right' | 'bottom' | 'center';
    alignment?: number;
    gap?: number;
    is_open?: boolean;
};

export class PopupComponent extends ComponentBase {
    state: Required<PopupState>;

    private anchorContainer: HTMLElement;
    private contentContainer: HTMLElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-popup');

        this.anchorContainer = document.createElement('div');
        this.anchorContainer.classList.add('rio-popup-anchor');
        this.anchorContainer.classList.add('rio-single-container');
        element.appendChild(this.anchorContainer);

        this.contentContainer = document.createElement('div');
        this.contentContainer.classList.add('rio-popup-content');
        this.contentContainer.classList.add('rio-single-container');
        element.appendChild(this.contentContainer);

        return element;
    }

    updateElement(element: HTMLElement, deltaState: PopupState): void {
        // Update the children
        replaceOnlyChild(element.id, this.anchorContainer, deltaState.anchor);
        replaceOnlyChild(element.id, this.contentContainer, deltaState.content);

        // Open / Close
        if (deltaState.is_open === true) {
            this.open();
        } else {
            element.classList.remove('rio-popup-open');
        }
    }

    open() {
        // Add the open class. This will trigger the CSS animation
        let element = this.element();
        element.classList.add('rio-popup-open');

        // The popup location is defined in developer-friendly terms. Convert
        // this to floats instead:
        //
        // - Anchor point X & Y (relative)
        // - Popup point X & Y (relative)
        // - Offset X & Y (absolute)
        //
        // The popup will appear, uch that the popup point is at the anchor
        // point. (But never off the screen.)
        let anchorRelativeX, anchorRelativeY;
        let contentRelativeX, contentRelativeY;
        let fixedOffsetXRem, fixedOffsetYRem;

        if (this.state.direction === 'left') {
            anchorRelativeX = 0;
            anchorRelativeY = this.state.alignment;
            contentRelativeX = 1;
            contentRelativeY = this.state.alignment;
            fixedOffsetXRem = -this.state.gap;
            fixedOffsetYRem = 0;
        } else if (this.state.direction === 'top') {
            anchorRelativeX = this.state.alignment;
            anchorRelativeY = 0;
            contentRelativeX = this.state.alignment;
            contentRelativeY = 1;
            fixedOffsetXRem = 0;
            fixedOffsetYRem = -this.state.gap;
        } else if (this.state.direction === 'right') {
            anchorRelativeX = 1;
            anchorRelativeY = this.state.alignment;
            contentRelativeX = 0;
            contentRelativeY = this.state.alignment;
            fixedOffsetXRem = this.state.gap;
            fixedOffsetYRem = 0;
        } else if (this.state.direction === 'bottom') {
            anchorRelativeX = this.state.alignment;
            anchorRelativeY = 1;
            contentRelativeX = this.state.alignment;
            contentRelativeY = 0;
            fixedOffsetXRem = 0;
            fixedOffsetYRem = this.state.gap;
        } else if (this.state.direction === 'center') {
            anchorRelativeX = 0.5;
            anchorRelativeY = 0.5;
            contentRelativeX = 0.5;
            contentRelativeY = 0.5;
            fixedOffsetXRem = 0;
            fixedOffsetYRem = 0;
        }

        // Determine the size of the screen
        let screenWidth = window.innerWidth;
        let screenHeight = window.innerHeight;

        // Determine the size of the Popup
        let anchorRect = this.anchorContainer.getBoundingClientRect();

        // Location of anchor
        let popupWidth = this.contentContainer.scrollWidth;
        let popupHeight = this.contentContainer.scrollHeight;

        // Where would the popup be positioned as requested by the user?
        let anchorPointX = anchorRect.left + anchorRect.width * anchorRelativeX;
        let anchorPointY = anchorRect.top + anchorRect.height * anchorRelativeY;

        let popupPointX = popupWidth * contentRelativeX;
        let popupPointY = popupHeight * contentRelativeY;

        let spawnPointX =
            anchorPointX - popupPointX + fixedOffsetXRem * pixelsPerEm;
        let spawnPointY =
            anchorPointY - popupPointY + fixedOffsetYRem * pixelsPerEm;

        // Establish limits, so the popup doesn't go off the screen. This is
        // relative to the popup's top left corner.
        let margin = 1 * pixelsPerEm;

        let minX = margin;
        let maxX = screenWidth - popupWidth - margin;

        let minY = margin;
        let maxY = screenHeight - popupHeight - margin;

        // Enforce limits
        spawnPointX = Math.min(Math.max(spawnPointX, minX), maxX);
        spawnPointY = Math.min(Math.max(spawnPointY, minY), maxY);

        // Set the position of the popup
        this.contentContainer.style.left = spawnPointX + 'px';
        this.contentContainer.style.top = spawnPointY + 'px';
    }
}
