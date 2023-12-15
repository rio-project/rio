import { pixelsPerEm } from '../app';
import { commitCss } from '../utils';
import { replaceOnlyChild } from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

// TODO
export type DrawerState = ComponentState & {
    _type_: 'Drawer-builtin';
    anchor?: number | string;
    content?: number | string;
    side?: 'left' | 'right' | 'top' | 'bottom';
    is_modal?: boolean;
    is_open?: boolean;
    is_user_openable?: boolean;
};

export class DrawerComponent extends ComponentBase {
    state: Required<DrawerState>;

    private anchorContainer: HTMLElement;
    private contentContainer: HTMLElement;
    private shadeElement: HTMLElement;

    private dragStartedAt: number = 0;
    private openFractionAtDragStart: number = 0;
    private openFraction: number = 1;
    private dragEventHandlers: Map<string, any> = new Map();

    private isFirstUpdate: boolean = true;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-drawer');

        this.anchorContainer = document.createElement('div');
        this.anchorContainer.classList.add('rio-drawer-anchor');
        this.anchorContainer.classList.add('rio-single-container');
        element.appendChild(this.anchorContainer);

        this.shadeElement = document.createElement('div');
        this.shadeElement.classList.add('rio-drawer-shade');
        element.appendChild(this.shadeElement);

        this.contentContainer = document.createElement('div');
        this.contentContainer.classList.add('rio-drawer-content');
        this.contentContainer.classList.add('rio-single-container');
        element.appendChild(this.contentContainer);

        return element;
    }

    updateElement(element: HTMLElement, deltaState: DrawerState): void {
        // Update the children
        replaceOnlyChild(element.id, this.anchorContainer, deltaState.anchor);
        replaceOnlyChild(element.id, this.contentContainer, deltaState.content);

        // Assign the correct class for the side
        if (deltaState.side !== undefined) {
            element.classList.remove('rio-drawer-left');
            element.classList.remove('rio-drawer-right');
            element.classList.remove('rio-drawer-top');
            element.classList.remove('rio-drawer-bottom');
            element.classList.add(`rio-drawer-${deltaState.side}`);
        }

        // Open?
        if (deltaState.is_open === true) {
            this.openFraction = 1;
        } else if (deltaState.is_open === false) {
            this.openFraction = 0;
        }

        // If user-openable, connect to events
        if (
            deltaState.is_user_openable === true &&
            (this.state.is_user_openable !== true || this.isFirstUpdate)
        ) {
            let beginDrag = this.beginDrag.bind(this);
            this.dragEventHandlers.set('mousedown', beginDrag);
            element.addEventListener('mousedown', beginDrag, true);
        } else if (
            deltaState.is_user_openable === false &&
            this.state.is_user_openable === true
        ) {
            for (let [name, handler] of this.dragEventHandlers) {
                element.removeEventListener(name, handler);
            }
        }

        // Make sure the CSS matches the state
        if (this.isFirstUpdate) {
            this._disableTransition();
        } else {
            this._enableTransition();
        }
        this._updateCss();

        // Not the first update anymore
        this.isFirstUpdate = false;
    }

    _updateCss() {
        // Account for the side of the drawer
        let axis =
            this.state.side === 'left' || this.state.side === 'right'
                ? 'X'
                : 'Y';

        let negate =
            this.state.side === 'right' || this.state.side === 'bottom'
                ? '+'
                : '-';

        // Move the drawer far enough to hide the shadow
        let closedFraction = 1 - this.openFraction;
        this.contentContainer.style.transform = `translate${axis}(calc(0rem ${negate} ${
            closedFraction * 100
        }% ${negate} ${closedFraction * 1}em))`;

        // Throw some shade, if modal
        if (this.state.is_modal) {
            let shadeFraction = this.openFraction * 0.5;
            this.shadeElement.style.backgroundColor = `rgba(0, 0, 0, ${shadeFraction})`;
            this.shadeElement.style.pointerEvents = this.state.is_open
                ? 'auto'
                : 'none';
        } else {
            this.shadeElement.style.backgroundColor = 'rgba(0, 0, 0, 0)';
            this.shadeElement.style.pointerEvents = 'none';
        }

        // Update the class
        let element = this.element();
        if (this.openFraction > 0.5) {
            element.classList.add('rio-drawer-open');
        } else {
            element.classList.remove('rio-drawer-open');
        }
    }

    _enableTransition() {
        // Remove the class and flush the style changes
        let element = this.element();
        element.classList.remove('rio-drawer-no-transition');
        commitCss(element);
    }

    _disableTransition() {
        // Add the class and flush the style changes
        let element = this.element();
        element.classList.add('rio-drawer-no-transition');
        commitCss(element);
    }

    openDrawer() {
        this.openFraction = 1;
        this._enableTransition();
        this._updateCss();

        // Notify the backend
        if (!this.state.is_open) {
            this.setStateAndNotifyBackend({
                is_open: true,
            });
        }
    }

    closeDrawer() {
        this.openFraction = 0;
        this._enableTransition();
        this._updateCss();

        // Notify the backend
        if (this.state.is_open) {
            this.setStateAndNotifyBackend({
                is_open: false,
            });
        }
    }

    beginDrag(event: MouseEvent) {
        let element = this.element();

        // Find the location of the drawer
        //
        // If the click was outside of the anchor element, ignore it
        let drawerRect = element.getBoundingClientRect();

        // Account for the side of the drawer
        const handleSizeIfClosed = 2.0 * pixelsPerEm;
        let relevantClickCoordinate, thresholdMin, thresholdMax;

        if (this.state.side === 'left') {
            relevantClickCoordinate = event.clientX;
            thresholdMin = drawerRect.left;
            thresholdMax = Math.max(
                drawerRect.left + handleSizeIfClosed,
                drawerRect.left +
                    this.contentContainer.scrollWidth * this.openFraction
            );
        } else if (this.state.side === 'right') {
            relevantClickCoordinate = event.clientX;
            thresholdMin = Math.min(
                drawerRect.right - handleSizeIfClosed,
                drawerRect.right -
                    this.contentContainer.scrollWidth * this.openFraction
            );
            thresholdMax = drawerRect.right;
        } else if (this.state.side === 'top') {
            relevantClickCoordinate = event.clientY;
            thresholdMin = drawerRect.top;
            thresholdMax = Math.max(
                drawerRect.top + handleSizeIfClosed,
                drawerRect.top +
                    this.contentContainer.scrollHeight * this.openFraction
            );
        } else if (this.state.side === 'bottom') {
            relevantClickCoordinate = event.clientY;
            thresholdMin = Math.min(
                drawerRect.bottom - handleSizeIfClosed,
                drawerRect.bottom -
                    this.contentContainer.scrollHeight * this.openFraction
            );
            thresholdMax = drawerRect.bottom;
        }

        // The drawer was clicked. It is being dragged now
        if (
            thresholdMin < relevantClickCoordinate &&
            relevantClickCoordinate < thresholdMax
        ) {
            this.openFractionAtDragStart = this.openFraction;
            this.dragStartedAt = relevantClickCoordinate;

            let moveHandler = this.dragMove.bind(this);
            this.dragEventHandlers.set('mousemove', moveHandler);
            window.addEventListener('mousemove', moveHandler, true);

            let upHandler = this.endDrag.bind(this);
            this.dragEventHandlers.set('mouseup', upHandler);
            this.dragEventHandlers.set('blur', upHandler);
            window.addEventListener('mouseup', upHandler, true);
            window.addEventListener('blur', upHandler, true);

            // Eat the event
            event.stopPropagation();
        }

        // The anchor was clicked. Collapse the drawer if modal
        else if (this.state.is_modal) {
            this.closeDrawer();

            // Eat the event
            event.stopPropagation();
        }
    }

    dragMove(event: MouseEvent) {
        // Account for the side of the drawer
        let relevantCoordinate, drawerSize;

        if (this.state.side === 'left' || this.state.side === 'right') {
            relevantCoordinate = event.clientX;
            drawerSize = this.contentContainer.scrollWidth;
        } else {
            relevantCoordinate = event.clientY;
            drawerSize = this.contentContainer.scrollHeight;
        }

        let negate =
            this.state.side === 'right' || this.state.side === 'bottom'
                ? -1
                : 1;

        // Calculate the fraction the drawer is open
        this.openFraction =
            this.openFractionAtDragStart +
            ((relevantCoordinate - this.dragStartedAt) / drawerSize) * negate;

        this.openFraction = Math.max(0, Math.min(1, this.openFraction));

        // Update the drawer
        this._disableTransition();
        this._updateCss();
    }

    endDrag() {
        // Snap to fully open or fully closed
        let threshold = this.openFractionAtDragStart > 0.5 ? 0.7 : 0.3;

        if (this.openFraction > threshold) {
            this.openDrawer();
        } else {
            this.closeDrawer();
        }

        // Remove the event handlers
        for (let [name, handler] of this.dragEventHandlers) {
            window.removeEventListener(name, handler, true);
        }
    }
}
