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
        //
        // Looking up elements via selector is wonky if the element has only
        // just been added. Give the browser time to update.
        setTimeout(() => setConnectionLostPopupVisible(false), 0);

        // Not really needed since this component will never see an update, but
        // here for consistency
        this.makeLayoutDirty();
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        // Don't use `window.innerWidth`. It appears to be rounded to the
        // nearest integer, so it's inaccurate.
        //
        // `getBoundingClientRect()` doesn't account for scroll bars, but our
        // <html> element is set to `overflow: hidden` anyway, so that's not an issue.
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
