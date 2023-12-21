import { pixelsPerEm } from '../app';
import {
    getElementByComponentId,
    replaceChildren,
} from '../componentManagement';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { setConnectionLostPopupVisible } from '../rpc';
import { ComponentBase, ComponentState } from './componentBase';

export type FundamentalRootComponentState = ComponentState & {
    _type_: 'FundamentalRootComponent-builtin';
    child: ComponentId;
    debugger: ComponentId | null;
    connection_lost_component: ComponentId;
};

export class FundamentalRootComponent extends ComponentBase {
    state: Required<FundamentalRootComponentState>;

    // The width and height for any components that want to span the entire
    // screen and not scroll. This differs from just the window width/height,
    // because the debugger can also take up space and doesn't count as part of
    // the user's app.
    public overlayWidth: number = 0;
    public overlayHeight: number = 0;

    private userRootWrapper: HTMLElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-fundamental-root-component');
        return element;
    }

    updateElement(
        element: HTMLElement,
        deltaState: FundamentalRootComponentState
    ): void {
        // Unlike what you'd expect, this function can actually be called more
        // than once. This is because of injected layout components; if the
        // user's root component changes, then its parent - this component right
        // here - is also updated. We don't actually need to do anything in that
        // case, so if we know that this function has already been executed
        // once, we'll abort.
        if (element.firstChild !== null) {
            return;
        }

        // Update the children
        let children = [deltaState.child, deltaState.connection_lost_component];

        if (deltaState.debugger !== null) {
            children.push(deltaState.debugger);
        }

        replaceChildren(element.id, element, children);

        // Initialize CSS
        this.userRootWrapper = document.createElement('div');
        this.userRootWrapper.appendChild(
            element.firstElementChild as HTMLElement
        );
        this.userRootWrapper.classList.add('rio-user-root-scroller');
        element.insertBefore(this.userRootWrapper, element.firstChild);

        let connectionLostPopupElement = element.children[1] as HTMLElement;
        connectionLostPopupElement.classList.add('rio-connection-lost-popup');

        if (deltaState.debugger !== null) {
            let debuggerElement = element.children[2] as HTMLElement;
            debuggerElement.classList.add('rio-debugger');
        }

        // Hide the connection lost popup by default
        setConnectionLostPopupVisible(false);

        // Not really needed since this component will never see an update, but
        // here for consistency
        this.makeLayoutDirty();
    }

    updateRequestedWidth(ctx: LayoutContext): void {
        // Don't use `window.innerWidth`. It appears to be rounded to the
        // nearest integer, so it's inaccurate.
        let rect = document.documentElement.getBoundingClientRect();
        this.requestedWidth = this.allocatedWidth = rect.width / pixelsPerEm;
        this.requestedHeight = this.allocatedHeight = rect.height / pixelsPerEm;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        // Overlays take up the full window
        this.overlayWidth = this.allocatedWidth;

        // If there's a debugger, account for that
        if (this.state.debugger !== null) {
            let dbg = ctx.inst(this.state.debugger);
            dbg.allocatedWidth = dbg.requestedWidth;
            this.overlayWidth -= dbg.allocatedWidth;
        }

        // The connection lost popup is an overlay
        let connectionLostPopup = ctx.inst(
            this.state.connection_lost_component
        );
        connectionLostPopup.allocatedWidth = this.overlayWidth;

        // The child may receive more than the overlay width, if it's larger
        // than the window. In that case, it will scroll.
        let child = ctx.inst(this.state.child);
        child.allocatedWidth = Math.max(
            child.requestedWidth,
            this.overlayWidth
        );
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        // Already done in updateRequestedWidth
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Overlays take up the full window
        this.overlayHeight = this.allocatedHeight;

        // If there's a debugger give it some space
        if (this.state.debugger !== null) {
            let dbgInst = ctx.inst(this.state.debugger);
            dbgInst.allocatedHeight = this.overlayHeight;

            // Position it
            let dbgElement = dbgInst.element();
            dbgElement.style.left = `${this.overlayWidth}rem`;
            dbgElement.style.top = '0';
        }

        // Size the user root wrapper
        this.userRootWrapper.style.width = `${this.overlayWidth}rem`;
        this.userRootWrapper.style.height = `${this.overlayHeight}rem`;

        // The connection lost popup is an overlay
        let connectionLostPopup = ctx.inst(
            this.state.connection_lost_component
        );
        connectionLostPopup.allocatedHeight = this.overlayHeight;

        // The child may once again receive more than the overlay height
        let child = ctx.inst(this.state.child);
        child.allocatedHeight = Math.max(
            child.requestedHeight,
            this.overlayHeight
        );
    }
}
