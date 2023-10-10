import { callRemoteMethodDiscardResponse } from "../rpc";

/// Base for all component states. Updates received from the backend are
/// partial, hence most properties may be undefined.
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

    // There are 3 different parties that can set the minimum size of a component:
    // 1. The user, by setting the `size`
    // 2. The implementation of the component
    // 3. The parent component
    //
    // This would be tricky to implement with pure CSS, so we keep track of
    // all of them with JS.
    protected _minSizeUser: [string | null, string | null];
    protected _minSizeComponentImpl: [string | null, string | null];
    protected _minSizeContainer: [string | null, string | null];

    constructor(elementId: string, state: Required<ComponentState>) {
        this.elementId = elementId;
        this.state = state;
        this.layoutCssProperties = {};

        this._minSizeUser = [null, null];
        this._minSizeComponentImpl = [null, null];
        this._minSizeContainer = [null, null];
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

    setMinSizeUser(minWidth: number | null, minHeight: number | null): void {
        this._minSizeUser = [
            minWidth === null ? null : `${minWidth}rem`,
            minHeight === null ? null : `${minHeight}rem`,
        ];
        this._updateMinSize();
    }

    setMinSizeComponentImpl(minWidth: string | null, minHeight: string | null): void {
        if (minWidth === '0' || minHeight === '0') {
            throw new Error(`Bare "0" is not allowed. You must add a unit.`);
        }

        this._minSizeComponentImpl = [minWidth, minHeight];
        this._updateMinSize();
    }

    setMinSizeContainer(minWidth: string | null, minHeight: string | null): void {
        if (minWidth === '0' || minHeight === '0') {
            throw new Error(`Bare "0" is not allowed. You must add a unit.`);
        }

        this._minSizeContainer = [minWidth, minHeight];
        this._updateMinSize();
    }

    private _updateMinSize(): void {
        let element = this.element();
        element.style.setProperty('min-width', this._buildMinSizeString(0));
        element.style.setProperty('min-height', this._buildMinSizeString(1));
    }

    private _buildMinSizeString(index: number): string {
        // This function could be simpler, but for debugging purposes it's nice
        // to see the values of all 3 sizes.
        let sizes = [
            this._minSizeUser[index],
            this._minSizeComponentImpl[index],
            this._minSizeContainer[index],
        ];

        if (sizes.every(size => size === null)) {
            return 'unset';
        }

        // Unfortunately, the string must be valid or it will be ignored. So we
        // can't just represent unset values as "null". We'll use "-1px"
        // instead.
        sizes = sizes.map(size => size ?? '-1px');

        return `max(${sizes.join(', ')})`;
    }

    /// Creates the HTML element associated with this component. This function does
    /// not attach the element to the DOM, but merely returns it.
    createElement(): HTMLElement {
        let element = this._createElement();

        element.id = this.elementId;

        return element;
    }

    abstract _createElement(): HTMLElement;

    /// Given a partial state update, this function updates the component's HTML
    /// element to reflect the new state.
    ///
    /// The `element` parameter is identical to `this.element()`. It's passed as
    /// an argument because it's more efficient than calling `this.element()`.
    updateElement(element: HTMLElement, deltaState: ComponentState): void {
        if (deltaState._size_ !== undefined) {
            let [width, height] = deltaState._size_;
            this.setMinSizeUser(width, height);
        }

        this._updateElement(element, deltaState);
    }

    abstract _updateElement(element: HTMLElement, deltaState: ComponentState): void;

    /// This method is called at the end of each `updateComponentStates`
    /// command. It is called for every component that was updated and every
    /// container that has a child that was updated.
    ///
    /// It is intended for containers that need to update the CSS of their
    /// children depending on the state of the children. For example, a `Row`
    /// needs to set `flex-grow` on its children depending on whether their
    /// width is `"grow"` or not.
    ///
    /// To assign CSS properties to a child, use the
    /// `child.replaceLayoutCssProperties() method. These properties will be
    /// automatically unset if the child is reparented by
    /// `replaceOnlyChildAndResetCssProperties` or
    /// `replaceChildrenAndResetCssProperties`.
    updateChildLayouts(): void { }

    /// Used by the parent for assigning the layout relevant CSS attributes to a
    /// child's HTML element. This function keeps track of the assigned
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

    /// Unsets all CSS properties that were set by the parent component.
    resetCssProperties(): void {
        this.replaceLayoutCssProperties({});
        this.setMinSizeContainer(null, null);
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
        this._updateElement(this.element(), deltaState);
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
