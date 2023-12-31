import { componentsById, getComponentByElement } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { callRemoteMethodDiscardResponse } from '../rpc';
import {
    EventHandler,
    DragHandler,
    DragHandlerArguments,
} from '../eventHandling';
import { DebuggerConnectorComponent } from './debuggerConnector';
import { ComponentId } from '../models';

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
    id: ComponentId;
    element: HTMLElement;

    state: Required<ComponentState>;

    // Reference to the parent component. If the component is about to be
    // removed from the widget tree (i.e. it's in `latent-components`), this
    // still references the *last* parent component. `null` is only for newly
    // created components and the root component.
    parent: ComponentBase | null = null;
    children = new Set<ComponentBase>();

    isLayoutDirty: boolean;

    naturalWidth: number;
    naturalHeight: number;

    requestedWidth: number;
    requestedHeight: number;

    allocatedWidth: number;
    allocatedHeight: number;

    _eventHandlers = new Set<EventHandler>();

    constructor(id: ComponentId, state: Required<ComponentState>) {
        this.id = id;
        this.state = state;

        this.element = this.createElement();
        this.element.classList.add('rio-component');

        this.isLayoutDirty = true;
    }

    /// Mark this element's layout as dirty, and chain up to the parent.
    makeLayoutDirty(): void {
        let cur: ComponentBase | null = this;

        while (cur !== null && !cur.isLayoutDirty) {
            cur.isLayoutDirty = true;
            cur = cur.parent;
        }
    }

    isInjectedLayoutComponent(): boolean {
        // Injected layout components have negative ids
        return this.id < 0;
    }

    getParentExcludingInjected(): ComponentBase | null {
        let parent: ComponentBase | null = this.parent;

        while (true) {
            if (parent === null) {
                return null;
            }

            if (!parent.isInjectedLayoutComponent()) {
                return parent;
            }

            parent = parent.parent;
        }
    }

    replaceOnlyChild(
        latentComponents: Set<ComponentBase>,
        childId: null | undefined | ComponentId,
        parentElement: HTMLElement = this.element
    ): void {
        // If undefined, do nothing
        if (childId === undefined) {
            return;
        }

        // If null, remove the current child
        const currentChildElement = parentElement.firstElementChild;

        if (childId === null) {
            if (currentChildElement !== null) {
                let child = getComponentByElement(currentChildElement);

                currentChildElement.remove();
                this.children.delete(child);
                latentComponents.add(child);

                this.makeLayoutDirty();
            }

            console.assert(parentElement.firstElementChild === null);
            return;
        }

        // If a child already exists, either move it to the latent container or
        // leave it alone if it's already the correct element
        if (currentChildElement !== null) {
            let child = getComponentByElement(currentChildElement);

            // Don't reparent the child if not necessary. This way things like
            // keyboard focus are preserved
            if (child.id === childId) {
                return;
            }

            currentChildElement.remove();
            this.children.delete(child);
            latentComponents.add(child);
        }

        // Add the replacement component
        let child = componentsById[childId]!;
        parentElement.appendChild(child.element);

        child.parent = this;
        this.children.add(child);
        latentComponents.delete(child);

        this.makeLayoutDirty();
    }

    replaceChildren(
        latentComponents: Set<ComponentBase>,
        childIds: undefined | ComponentId[],
        parentElement: HTMLElement = this.element,
        wrapInDivs: boolean = false
    ): void {
        // If undefined, do nothing
        if (childIds === undefined) {
            return;
        }

        let dirty = false;

        let curElement = parentElement.firstElementChild;
        let children = childIds.map((id) => componentsById[id]!);
        let curIndex = 0;

        let wrap: (element: HTMLElement) => Element;
        let unwrap: (element: Element) => HTMLElement;
        if (wrapInDivs) {
            wrap = (element: HTMLElement) => {
                let wrapper = document.createElement('div');
                wrapper.appendChild(element);
                return wrapper;
            };
            unwrap = (element: Element) =>
                element.firstElementChild as HTMLElement;
        } else {
            wrap = (element: HTMLElement) => element;
            unwrap = (element: Element) => element as HTMLElement;
        }

        while (true) {
            // If there are no more children in the DOM element, add the remaining
            // children
            if (curElement === null) {
                while (curIndex < children.length) {
                    let child = children[curIndex];

                    parentElement.appendChild(wrap(child.element));
                    child.parent = this;
                    this.children.add(child);
                    latentComponents.delete(child);

                    dirty = true;
                    curIndex++;
                }
                break;
            }

            // If there are no more children in the message, remove the
            // remaining DOM children
            if (curIndex >= children.length) {
                while (curElement !== null) {
                    let nextElement = curElement.nextElementSibling;

                    curElement.remove();

                    let child = getComponentByElement(unwrap(curElement));
                    latentComponents.add(child);
                    this.children.delete(child);

                    dirty = true;
                    curElement = nextElement;
                }
                break;
            }

            // If this element is the correct element, move on
            let curChild = getComponentByElement(unwrap(curElement));
            let expectedChild = children[curIndex];
            if (curChild === expectedChild) {
                curElement = curElement.nextElementSibling;
                curIndex++;
                continue;
            }

            // This element is not the correct element, insert the correct one
            // instead
            parentElement.insertBefore(wrap(expectedChild.element), curElement);
            expectedChild.parent = this;
            this.children.add(expectedChild);
            latentComponents.delete(expectedChild);

            curIndex++;
            dirty = true;
        }

        if (dirty) {
            this.makeLayoutDirty();
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
    abstract updateElement(
        deltaState: ComponentState,
        latentComponents: Set<ComponentBase>
    ): void;

    /// Send a message to the python instance corresponding to this component. The
    /// message is an arbitrary JSON object and will be passed to the instance's
    /// `_on_message` method.
    sendMessageToBackend(message: object): void {
        callRemoteMethodDiscardResponse('componentMessage', {
            componentId: this.id,
            payload: message,
        });
    }

    _setStateDontNotifyBackend(deltaState: ComponentState): void {
        // Trigger an update
        this.updateElement(deltaState, null as any as Set<ComponentBase>);

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
            componentId: this.id,
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

    addDragHandler(args: DragHandlerArguments): DragHandler {
        return new DragHandler(this, args);
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

globalThis.RIO_COMPONENT_BASE = ComponentBase;
