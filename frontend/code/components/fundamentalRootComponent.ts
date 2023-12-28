import { pixelsPerEm } from '../app';
import { componentsById } from '../componentManagement';
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

    public rootScrollerElement: HTMLElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-fundamental-root-component');
        return element;
    }

    updateElement(deltaState: FundamentalRootComponentState): void {
        // Unlike what you'd expect, this function can actually be called more
        // than once. This is because of injected layout components; if the
        // user's root component changes, then its parent - this component right
        // here - is also updated. We don't actually need to do anything in that
        // case, so if we know that this function has already been executed
        // once, we'll abort.
        if (this.element.firstChild !== null) {
            return;
        }

        // Update the children
        let children = [deltaState.child, deltaState.connection_lost_component];

        if (deltaState.debugger !== null) {
            children.push(deltaState.debugger);
        }

        this.replaceChildren(children);

        // Initialize CSS
        this.rootScrollerElement = document.createElement('div');
        this.rootScrollerElement.appendChild(
            this.element.firstElementChild as HTMLElement
        );
        this.rootScrollerElement.classList.add('rio-user-root-scroller');
        this.element.insertBefore(
            this.rootScrollerElement,
            this.element.firstChild
        );

        let connectionLostPopupElement = this.element
            .children[1] as HTMLElement;
        connectionLostPopupElement.classList.add('rio-connection-lost-popup');

        if (deltaState.debugger !== null) {
            let debuggerElement = this.element.children[2] as HTMLElement;
            debuggerElement.classList.add('rio-debugger');
        }

        // Hide the connection lost popup by default
        setConnectionLostPopupVisible(false);

        // Not really needed since this component will never see an update, but
        // here for consistency
        this.makeLayoutDirty();
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        // Don't use `window.innerWidth`. It appears to be rounded to the
        // nearest integer, so it's inaccurate.
        let rect = document.documentElement.getBoundingClientRect();
        this.naturalWidth = this.allocatedWidth = rect.width / pixelsPerEm;
        this.naturalHeight = this.allocatedHeight = rect.height / pixelsPerEm;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        // Overlays take up the full window
        this.overlayWidth = this.allocatedWidth;

        // If there's a debugger, account for that
        if (this.state.debugger !== null) {
            let dbg = componentsById[this.state.debugger]!;
            dbg.allocatedWidth = dbg.requestedWidth;
            this.overlayWidth -= dbg.allocatedWidth;
        }

        // The connection lost popup is an overlay
        let connectionLostPopup =
            componentsById[this.state.connection_lost_component]!;
        connectionLostPopup.allocatedWidth = this.overlayWidth;

        // The child may receive more than the overlay width, if it's larger
        // than the window. In that case, it will scroll.
        let child = componentsById[this.state.child]!;
        child.allocatedWidth = Math.max(
            child.requestedWidth,
            this.overlayWidth
        );
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        // Already done in updateNaturalWidth
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Overlays take up the full window
        this.overlayHeight = this.allocatedHeight;

        // If there's a debugger give it some space
        if (this.state.debugger !== null) {
            let dbgInst = componentsById[this.state.debugger]!;
            dbgInst.allocatedHeight = this.overlayHeight;

            // Position it
            let dbgElement = dbgInst.element;
            dbgElement.style.left = `${this.overlayWidth}rem`;
            dbgElement.style.top = '0';
        }

        // Size the user root wrapper
        this.rootScrollerElement.style.width = `${this.overlayWidth}rem`;
        this.rootScrollerElement.style.height = `${this.overlayHeight}rem`;

        // The connection lost popup is an overlay
        let connectionLostPopup =
            componentsById[this.state.connection_lost_component]!;
        connectionLostPopup.allocatedHeight = this.overlayHeight;

        // The child may once again receive more than the overlay height
        let child = componentsById[this.state.child]!;
        child.allocatedHeight = Math.max(
            child.requestedHeight,
            this.overlayHeight
        );
    }
}
