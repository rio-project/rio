import {
    componentsById,
    getChildIds,
    getComponentByElement,
    getParentComponentElementIncludingInjected,
} from '../componentManagement';
import { LayoutContext } from '../layouting';
import { callRemoteMethodDiscardResponse } from '../rpc';
import { EventHandler, DragHandler } from '../eventHandling';
import { ComponentTreeComponent } from './componentTree';
import { DebuggerConnectorComponent } from './debuggerConnector';

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
    id: string;
    element: HTMLElement;

    state: Required<ComponentState>;

    isLayoutDirty: boolean;

    naturalWidth: number;
    naturalHeight: number;

    requestedWidth: number;
    requestedHeight: number;

    allocatedWidth: number;
    allocatedHeight: number;

    private _eventHandlers: EventHandler[] = [];

    constructor(id: string, state: Required<ComponentState>) {
        this.id = id;
        this.state = state;

        this.element = this.createElement();
        this.element.id = `rio-id-${id}`;
        this.element.classList.add('rio-component');

        this.isLayoutDirty = true;
    }

    /// Returns the children of this component. Slowish.
    getDirectChildren(): ComponentBase[] {
        return getChildIds(this.state).map((id) => componentsById[id]!);
    }

    /// Returns this element's parent. Returns `null` if this element has no
    /// parent.
    tryGetParent(): ComponentBase | null {
        let parentElement = getParentComponentElementIncludingInjected(
            this.element
        );

        if (parentElement === null) {
            return null;
        }

        return getComponentByElement(parentElement);
    }

    /// Mark this element's layout as dirty, and chain up to the parent.
    makeLayoutDirty(): void {
        let cur: ComponentBase | null = this;

        while (cur !== null && !cur.isLayoutDirty) {
            cur.isLayoutDirty = true;
            cur = cur.tryGetParent();
        }
    }

    /// Creates the HTML element associated with this component. This function does
    /// not attach the element to the DOM, but merely returns it.
    protected abstract createElement(): HTMLElement;

    /// This method is called when a component is about to be removed from the
    /// widget tree. It can be used for cleaning up event handlers and helper
    /// HTML elements (like popups).
    onDestruction(): void {
        for (let handler of this._eventHandlers) {
            handler.disconnect();
        }
    }

    /// Given a partial state update, this function updates the component's HTML
    /// element to reflect the new state.
    ///
    /// The `element` parameter is identical to `this.element`. It's passed as
    /// an argument because it's more efficient than calling `this.element`.
    abstract updateElement(deltaState: ComponentState): void;

    /// Send a message to the python instance corresponding to this component. The
    /// message is an arbitrary JSON object and will be passed to the instance's
    /// `_on_message` method.
    sendMessageToBackend(message: object): void {
        callRemoteMethodDiscardResponse('componentMessage', {
            componentId: parseInt(this.id),
            payload: message,
        });
    }

    _setStateDontNotifyBackend(deltaState: ComponentState): void {
        // Trigger an update
        this.updateElement(deltaState);

        // Set the state
        this.state = {
            ...this.state,
            ...deltaState,
        };
    }

    setStateAndNotifyBackend(deltaState: object): void {
        // Set the state. This also updates the component
        this._setStateDontNotifyBackend(deltaState);

        // Notify the backend
        callRemoteMethodDiscardResponse('componentStateUpdate', {
            componentId: parseInt(this.id),
            deltaState: deltaState,
        });

        // Notify the debugger, if any
        if (globalThis.RIO_DEBUGGER !== null) {
            let debuggerTree =
                globalThis.RIO_DEBUGGER as DebuggerConnectorComponent;

            debuggerTree.afterComponentStateChange({
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

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth = 0;
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        this.naturalHeight = 0;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {}
    updateAllocatedHeight(ctx: LayoutContext): void {}
}

globalThis.ComponentBase = ComponentBase;
