/// Base for all component states. Updates received from the backend are partial,

import { callRemoteMethodDiscardResponse } from '../rpc';

/// hence most properties may be undefined.
export type ComponentState = {
    _type_?: string;
    _python_type_?: string;
    _key_?: string;
    _margin_?: [number, number, number, number];
    _size_?: [number | null, number | null];
    _align_?: [number | null, number | null];
    _grow_?: [boolean, boolean];
};

/// Base class for all components
export abstract class ComponentBase {
    elementId: string;
    state: Required<ComponentState>;
    layoutCssProperties: object;

    constructor(elementId: string, state: ComponentState) {
        this.elementId = elementId;
        this.state = state as Required<ComponentState>;
        this.layoutCssProperties = {};
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

    /// Given a partial state update, this function updates the component's HTML
    /// element to reflect the new state.
    ///
    /// The `element` parameter is identical to `this.element`. Calling that
    /// property is slow however, so it is passed as argument here, to avoid
    /// accidentally calling the property multiple times.
    abstract updateElement(
        element: HTMLElement,
        deltaState: ComponentState
    ): void;

    /// Update the layout relevant CSS attributes for all of the component's
    /// children.
    updateChildLayouts(): void {}

    /// Used by the parent for assigning the layout relevant CSS attributes to
    /// the component's HTML element. This function keeps track of the assigned
    /// properties, allowing it to remove properties which are no longer
    /// relevant.
    replaceLayoutCssProperties(cssProperties: object): void {
        let element = this.element();

        // Find all properties which are no longer present and remove them
        for (let key in this.layoutCssProperties) {
            if (!(key in cssProperties)) {
                element.style.removeProperty(key);
            }
        }

        // Set all properties which are new or changed
        for (let key in cssProperties) {
            element.style.setProperty(key, cssProperties[key]);
        }

        // Keep track of the new properties
        this.layoutCssProperties = cssProperties;
    }

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

        // Notify the backend
        callRemoteMethodDiscardResponse('componentStateUpdate', {
            // Remove the leading `rio-id-` from the element's ID
            componentId: parseInt(this.elementId.substring('rio-id-'.length)),
            deltaState: deltaState,
        });
    }
}

globalThis.ComponentBase = ComponentBase;
