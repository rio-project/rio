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
};

/// Base class for all widgets
export abstract class WidgetBase {
    elementId: string;
    state: object;

    constructor(elementId: string, state: WidgetState) {
        this.elementId = elementId;
        this.state = state;
    }

    /// Fetches the HTML element associated with this widget. This is a slow
    /// operation and should be avoided if possible.
    get element() {
        let element = document.getElementById(this.elementId);

        if (element === null) {
            throw new Error(
                `Instance for element with id ${this.elementId} cannot find its element`
            );
        }

        return element;
    }

    /// Creates the HTML element associated with this widget. This function does
    /// not attach the element to the DOM, but merely returns it.
    abstract createElement(): HTMLElement;

    /// Given a partial state update, this function updates the widget's HTML
    /// element to reflect the new state.
    ///
    /// The `element` parameter is identical to `this.element`. Calling that
    /// property is slow however, so it is passed as argument here, to avoid
    /// accidentally calling the property multiple times.
    abstract updateElement(element: HTMLElement, deltaState: WidgetState): void;

    /// Send a message to the python instance corresponding to this widget. The
    /// message is an arbitrary JSON object and will be passed to the instance's
    /// `_on_message` method.
    sendMessageToBackend(message: object) {
        sendMessageOverWebsocket({
            type: 'widgetMessage',
            // Remove the leading `reflex-id-` from the element's ID
            widgetId: parseInt(this.elementId.substring(10)),
            payload: message,
        });
    }
}

globalThis.WidgetBase = WidgetBase;
