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

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-fundamental-root-component');
        return element;
    }

    updateElement(
        deltaState: FundamentalRootComponentState,
        latentComponents: Set<ComponentBase>
    ): void {
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

        this.replaceChildren(latentComponents, children);

        // Initialize CSS
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
        // We have a bunch of problems here:
        // 1. `window.innerWidth` isn't accurate. (It seems to be rounded to the
        //    nearest integer.)
        // 2. `document.documentElement.getBoundingClientRect().width` is
        //    accurate, but excludes space reserved for a scroll bar. (The
        //    window should never have a scroll bar, and yet it does. No idea
        //    why. To reproduce, simply open your browser console - there'll be
        //    unallocated space on the right-hand side.)
        // 3. Whatever measurement we get is in pixels, but we need it in rem.
        //    We divide it to get rem, then the browser multiplies it to get
        //    pixels. Floating point inaccuracies can happen in this process. We
        //    must ensure that the content always fits on the screen, otherwise
        //    the browser will create scroll bars and screw up our layouting.

        // I can't think of a better solution ¯\_(ツ)_/¯
        this.naturalWidth = this.allocatedWidth =
            (window.innerWidth - 2) / pixelsPerEm;
        this.naturalHeight = this.allocatedHeight =
            (window.innerHeight - 2) / pixelsPerEm;
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

        // The child receives the remaining width. (The child is a
        // ScrollContainer, it takes care of scrolling if the user content is
        // too large)
        let child = componentsById[this.state.child]!;
        child.allocatedWidth = this.overlayWidth;

        // Despite being an overlay, the connection lost popup should also cover
        // the debugger
        let connectionLostPopup =
            componentsById[this.state.connection_lost_component]!;
        connectionLostPopup.allocatedWidth = this.allocatedWidth;
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        // Already done in updateNaturalWidth
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Overlays take up the full window
        this.overlayHeight = this.allocatedHeight;

        // If there's a debugger, set its height and position it
        if (this.state.debugger !== null) {
            let dbgInst = componentsById[this.state.debugger]!;
            dbgInst.allocatedHeight = this.overlayHeight;

            // Position it
            let dbgElement = dbgInst.element;
            dbgElement.style.left = `${this.overlayWidth}rem`;
            dbgElement.style.top = '0';
        }

        // The connection lost popup is an overlay
        let connectionLostPopup =
            componentsById[this.state.connection_lost_component]!;
        connectionLostPopup.allocatedHeight = this.overlayHeight;

        // The child once again receives the remaining width. (The child is a
        // ScrollContainer, it takes care of scrolling if the user content is
        // too large)
        let child = componentsById[this.state.child]!;
        child.allocatedHeight = this.overlayHeight;
    }
}
