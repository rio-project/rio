import { sendMessageOverWebsocket } from './app';

/// Base for all widget states. Updates received from the backend are partial,
/// hence most properties may be undefined.
export type WidgetState = {
    _type_: string;
    _python_type_: string;
    _key_?: string;
    _margin_?: [number, number, number, number];
    _size_?: [number | null, number | null];
    _align_?: [number | null, number | null];
    _grow_?: [boolean, boolean];
};

/// Base class for all widgets
export abstract class WidgetBase {
    outerElementId: string;
    state: object;

    constructor(outerElementId: string, state: WidgetState) {
        this.outerElementId = outerElementId;
        this.state = state;
    }

    /// Fetches the HTML element associated with this widget. This is a slow
    /// operation and should be avoided if possible.
    get innerElement() {
        return this.outerElement.firstElementChild as HTMLElement;
    }

    get outerElement() {
        let element = document.getElementById(this.outerElementId);

        if (element === null) {
            throw new Error(
                `Instance for element with id ${this.outerElementId} cannot find its element`
            );
        }

        return element;
    }

    /// Creates the HTML element associated with this widget. This function does
    /// not attach the element to the DOM, but merely returns it.
    abstract createInnerElement(): HTMLElement;

    /// Given a partial state update, this function updates the widget's HTML
    /// element to reflect the new state.
    ///
    /// The `element` parameter is identical to `this.element`. Calling that
    /// property is slow however, so it is passed as argument here, to avoid
    /// accidentally calling the property multiple times.
    abstract updateInnerElement(
        element: HTMLElement,
        deltaState: WidgetState
    ): void;

    /// Send a message to the python instance corresponding to this widget. The
    /// message is an arbitrary JSON object and will be passed to the instance's
    /// `_on_message` method.
    sendMessageToBackend(message: object) {
        sendMessageOverWebsocket({
            type: 'widgetMessage',
            // Remove the leading `reflex-id-` from the element's ID
            widgetId: parseInt(this.outerElementId.substring(10)),
            payload: message,
        });
    }

    _setStateDontNotifyBackend(deltaState: object) {
        // Set the state
        this.state = {
            ...this.state,
            ...deltaState,
        };

        // Trigger an update
        // @ts-ignore
        this.updateInnerElement(this.innerElement, deltaState);
    }

    setStateAndNotifyBackend(deltaState: object) {
        // Set the state. This also updates the widget
        this._setStateDontNotifyBackend(deltaState);

        // Notify the backend
        sendMessageOverWebsocket({
            type: 'widgetStateUpdate',
            // Remove the leading `reflex-id-` from the element's ID
            widgetId: parseInt(this.outerElementId.substring(10)),
            deltaState: deltaState,
        });
    }
}

globalThis.WidgetBase = WidgetBase;
