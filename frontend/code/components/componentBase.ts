import {
    getChildIds,
    getInstanceByComponentId,
    getInstanceByElement,
    getParentComponentElementIncludingInjected,
} from '../componentManagement';
import { LayoutContext } from '../layouting';
import { callRemoteMethodDiscardResponse } from '../rpc';
import { EventHandler, DragHandler } from '../eventHandling';

/// Base for all component states. Updates received from the backend are
/// partial, hence most properties may be undefined.
export type ComponentState = {
    // The component type's unique id. Crucial so the client knows what kind of
    // component to spawn.
    _type_?: string;
    // Debugging information. Useful both for developing rio itself, and also
    // displayed to developers in Rio's debugger
    _python_type_?: string;
    // Debugging information
    _key_?: string | null;
    // How much space to leave on the left, top, right, bottom
    _margin_?: [number, number, number, number];
    // Explicit size request, if any
    _size_?: [number, number];
    // Alignment of the component within its parent, if any
    _align_?: [number | null, number | null];
    // Whether the component would like to receive additional space if there is
    // any left over
    _grow_?: [boolean, boolean];
    // Debugging information: The debugger may not display components to the
    // developer if they're considered internal
    _rio_internal_?: boolean;
};

/// Base class for all components
///
/// Note: Components that can have the keyboard focus must also implement a
/// `grabKeyboardFocus(): void` method.
export abstract class ComponentBase {
    elementId: string;
    state: Required<ComponentState>;

    isLayoutDirty: boolean;

    requestedWidth: number;
    requestedHeight: number;

    allocatedWidth: number;
    allocatedHeight: number;

    private _eventHandlers: EventHandler[] = [];

    constructor(elementId: string, state: Required<ComponentState>) {
        this.elementId = elementId;
        this.state = state;

        this.isLayoutDirty = true;

        this.requestedWidth = 0;
        this.requestedHeight = 0;

        this.allocatedWidth = 0;
        this.allocatedHeight = 0;
    }

    /// Returns the children of this component. Slowish.
    getDirectChildren(): ComponentBase[] {
        return getChildIds(this.state).map(getInstanceByComponentId);
    }

    /// Returns this element's parent. Returns `null` if this element has no
    /// parent.
    tryGetParent(): ComponentBase | null {
        let parentElement = getParentComponentElementIncludingInjected(
            this.element()
        );

        if (parentElement === null) {
            return null;
        }

        return getInstanceByElement(parentElement);
    }

    /// Mark this element's layout as dirty, and chain up to the parent.
    makeLayoutDirty(): void {
        let cur: ComponentBase | null = this;

        while (cur !== null && !cur.isLayoutDirty) {
            cur.isLayoutDirty = true;
            cur = cur.tryGetParent();
        }
    }


    /// Fetches the HTML element associated with this component. This is a slow
    /// operation and should be avoided if possible. Returns `null` if the
    /// element cannot be found.
    tryGetElement(): HTMLElement | null {
        return document.getElementById(this.elementId);
    }

    /// Fetches the HTML element associated with this component. This is a slow
    /// operation and should be avoided if possible. It is an error to look up
    /// an element which does not exist.
    element(): HTMLElement {
        let element = document.getElementById(this.elementId);

        if (element === null) {
            throw new Error(
                `Instance for ${this.state._python_type_} component with id ${this.elementId} cannot find its element`
            );
        }

        return element;
    }

    /// Creates the HTML element associated with this component. This function does
    /// not attach the element to the DOM, but merely returns it.
    abstract createElement(): HTMLElement;

    /// This method is called after the component's HTML element has been
    /// created. It is intended for components that need to do some additional
    /// initialization once they know their initial state.
    onCreation(element: HTMLElement, state: Required<ComponentState>): void {}

    /// This method is called right before the component's HTML element is
    /// removed from the DOM. It can be used for cleaning up event handlers and
    /// helper HTML elements (like popups).
    onDestruction(element: HTMLElement): void {
        for (let handler of this._eventHandlers) {
            handler.disconnect();
        }
    }

    /// Given a partial state update, this function updates the component's HTML
    /// element to reflect the new state.
    ///
    /// The `element` parameter is identical to `this.element()`. It's passed as
    /// an argument because it's more efficient than calling `this.element()`.
    abstract updateElement(
        element: HTMLElement,
        deltaState: ComponentState
    ): void;

    /// Send a message to the python instance corresponding to this component. The
    /// message is an arbitrary JSON object and will be passed to the instance's
    /// `_on_message` method.
    sendMessageToBackend(message: object): void {
        callRemoteMethodDiscardResponse('componentMessage', {
            // Remove the leading `rio-id-` from the element's ID
            componentId: parseInt(this.elementId.substring('rio-id-'.length)),
            payload: message,
        });
    }

    _setStateDontNotifyBackend(deltaState: object): void {
        // Set the state
        this.state = {
            ...this.state,
            ...deltaState,
        };

        // Trigger an update
        // @ts-ignore
        this.updateElement(this.element(), deltaState);
    }

    setStateAndNotifyBackend(deltaState: object): void {
        // Set the state. This also updates the component
        this._setStateDontNotifyBackend(deltaState);

        // Remove the leading `rio-id-` from the element's ID
        let componentIdString = this.elementId.substring('rio-id-'.length);
        let componentIdInt = parseInt(componentIdString);

        // Notify the backend
        callRemoteMethodDiscardResponse('componentStateUpdate', {
            componentId: componentIdInt,
            deltaState: deltaState,
        });

        // Notify the debugger, if any
        if (globalThis.rioDebugger !== undefined) {
            globalThis.rioDebugger.afterComponentStateChange({
                componentIdString: deltaState,
            });
        }
    }

    addDragHandler(
        element: HTMLElement,
        onStart: null | ((event: MouseEvent) => void) = null,
        onMove: null | ((event: MouseEvent) => void) = null,
        onEnd: null | ((event: MouseEvent) => void) = null
    ): DragHandler {
        let handler = new DragHandler(element, onStart, onMove, onEnd);
        this._eventHandlers.push(handler);
        return handler;
    }

    updateRequestedWidth(ctx: LayoutContext): void {
        this.requestedWidth = 0;
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        this.requestedHeight = 0;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {}
    updateAllocatedHeight(ctx: LayoutContext): void {}
}

globalThis.ComponentBase = ComponentBase;
