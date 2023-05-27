import { pixelsPerEm, replaceOnlyChild, sendEventOverWebsocket } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

function eventMouseButtonToString(event: MouseEvent): object {
    return {
        button: ['left', 'middle', 'right'][event.button],
    };
}

function eventMousePositionToString(event: MouseEvent): object {
    return {
        x: event.clientX / pixelsPerEm,
        y: event.clientY / pixelsPerEm,
    };
}

export type MouseEventListenerState = WidgetState & {
    _type_: 'mouseEventListener';
    child?: number;
    reportMouseDown?: boolean;
    reportMouseUp?: boolean;
    reportMouseMove?: boolean;
    reportMouseEnter?: boolean;
    reportMouseLeave?: boolean;
};

export class MouseEventListenerWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-mouse-event-listener');
        return element;
    }

    updateElement(
        element: HTMLElement,
        deltaState: MouseEventListenerState
    ): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.reportMouseDown) {
            element.onmousedown = (e) => {
                sendEventOverWebsocket(element, 'mouseDownEvent', {
                    ...eventMouseButtonToString(e),
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmousedown = null;
        }

        if (deltaState.reportMouseUp) {
            element.onmouseup = (e) => {
                sendEventOverWebsocket(element, 'mouseUpEvent', {
                    ...eventMouseButtonToString(e),
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmouseup = null;
        }

        if (deltaState.reportMouseMove) {
            element.onmousemove = (e) => {
                sendEventOverWebsocket(element, 'mouseMoveEvent', {
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmousemove = null;
        }

        if (deltaState.reportMouseEnter) {
            element.onmouseenter = (e) => {
                sendEventOverWebsocket(element, 'mouseEnterEvent', {
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmouseenter = null;
        }

        if (deltaState.reportMouseLeave) {
            element.onmouseleave = (e) => {
                sendEventOverWebsocket(element, 'mouseLeaveEvent', {
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmouseleave = null;
        }
    }
}
